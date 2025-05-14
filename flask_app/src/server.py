from itertools import groupby
import json
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from flask import Flask, render_template, request, send_from_directory

from modules import ConferenceModule, read_modules, get_all_tags
from win32_powerpoint_builder import create_conference_slides
import webview
from config import get_conference_and_modules_path, get_gui_path, get_assets_path


server = Flask(__name__, static_url_path='/static', static_folder=get_conference_and_modules_path(), template_folder=get_gui_path())
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1 

@dataclass
class Conference:
    title: str
    subtitle: str
    modules: list[int]

conference_modules: list[ConferenceModule] = read_modules(get_conference_and_modules_path())
conference = Conference(title='Ma conférence', subtitle='Accroche', modules=[])

@server.route('/')
def landing():
    """
    Render index.html. Initialization is performed asynchronously in initialize() function
    """
    return render_template('index.html', 
                           modules_list=render_modules_list(conference_modules), 
                           conference=render_conference(get_current_conference()), 
                           tags_categories=get_all_tags(conference_modules))


@server.route('/add-module/<int:module_id>', methods=['POST'])
def add_module(module_id):
    c = get_current_conference()
    c.modules.append(module_id)
    set_current_conference(c)
    return render_conference(c)

@server.route('/move/<int:module_index>/<int:new_index>', methods=['POST'])
def move_module(module_index, new_index):
    c = get_current_conference()
    c.modules[module_index], c.modules[new_index] = c.modules[new_index], c.modules[module_index]
    set_current_conference(c)
    return render_conference(c)

@server.route('/module/<int:module_index>', methods=['DELETE'])
def remove_module(module_index):
    c = get_current_conference()
    c.modules.pop(module_index)
    set_current_conference(c)
    return render_conference(c)

@server.route('/reset', methods=['POST'])
def reset():
    new_conference = Conference(modules=[])
    set_current_conference(new_conference)
    return render_conference(new_conference)

@server.route('/conference-settings', methods=['PUT'])
def set_conference_settings():
    c = get_current_conference()
    c.title = request.form.get("title")
    c.subtitle = request.form.get("subtitle")
    set_current_conference(c)
    return render_template('conference_settings.html', conference_title=c.title, conference_subtitle=c.subtitle)

@server.route('/download', methods=['POST'])
def download():
    c = get_current_conference()
    modules = [next(m for m in conference_modules if m.id == id) for id in c.modules]

    file = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_conference.pptx')
    if file and len(file) > 0:
        create_conference_slides(
            modules, 
            title=c.title, 
            subtitle=c.subtitle, 
            date=datetime.now().strftime("%d/%m/%Y"), 
            save_path=file
        )

    return ''

@server.route('/export', methods=['POST'])
def export():
    serialized = serialize_conference(get_current_conference())
    file = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_conference.focon')
    with open(file, "w") as text_file:
        text_file.write(serialized)
    return ''

@server.route('/import', methods=['POST'])
def import_conference():
    files = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG)
    if files and len(files) > 0:
        filename = files[0]
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')
        with open(filename) as file:
            set_current_conference(deserialize_conference(file.read()))
    return render_conference(get_current_conference())

@server.route('/search-modules', methods=['GET'])
def search_modules():
    search = request.args.get("search")
    return render_modules_list(conference_modules, search)


def get_current_conference() -> Conference:
    return conference

def set_current_conference(c: Conference):
    global conference
    conference = c

def render_modules_list(modules: list[ConferenceModule], search: str | None = None):
    if search:
        search = search.lower()
        modules = filter(lambda module: search in module.title.lower() or search in module.description.lower(), conference_modules)
    modules = list(modules)
    modules.sort(key=lambda m: m.title)
    return render_template('modules_list.html', modules=modules)

def render_conference(c: Conference):
    modules: list[ConferenceModule] = [next(m for m in conference_modules if m.id == id) for id in c.modules]
    modules_data = [
        {
            "image_url": module.img_url,
            "title": module.title,
            "description": module.description,
            "duration_minutes": module.duration_minutes,
            "tags_categories": [ { "category": k, "tags": [tag.tag for tag in v] } for k, v in groupby(module.tags, lambda t:t.category) ],
            "previous": idx -1,
            "next": idx + 1
        } for idx, module in enumerate(modules)
    ]
    total_duration = np.sum([module.duration_minutes for module in modules])

    # conference_module_tags = ConferenceModuleTag.objects.order_by('tag__category', 'tag__name').filter(conference_module__in=[module.id for module in modules]).select_related('tag', 'tag__category', 'conference_module')
    # tags_grouped_by_category = groupby([{ "tag": cm.tag, "duration_minutes": cm.tag_category_importance * cm.conference_module.duration_minutes } for cm in conference_module_tags], lambda t:t["tag"].category.name)
    # categories_tags_repartition = [ { "category": category, "tags": [{"tag": tag, "duration_minutes": np.sum([occ["duration_minutes"] for occ in tag_details])} for tag, tag_details in groupby(tags_details, lambda item: item["tag"].name)] } for category, tags_details in tags_grouped_by_category ]
    return render_template('conference.html', conference_title=c.title, conference_subtitle=c.subtitle, modules=modules_data, stats={
        "duration_minutes": total_duration,
        "categories_tags_repartition": []
    })

def serialize_conference(conference: Conference) -> str:
    to_export = {
        "modules": conference.modules,
        "title": conference.title,
        "subtitle": conference.subtitle,
        "version": 1
    }
    return json.dumps(to_export)

def deserialize_conference(serialized: str) -> Conference:
    parsed = json.loads(serialized)
    return Conference(
        modules=parsed["modules"], 
        title=parsed["title"] if "title" in parsed else "", 
        subtitle=parsed["subtitle"] if "subtitle" in parsed else ""
    )


@server.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory(get_assets_path(), filename)