import os
from dataclasses import dataclass
import numpy as np

from flask import Flask, render_template

from modules import ConferenceModule, read_modules
from win32_powerpoint_builder import merge_presentations
import webview
from config import get_assets_path, get_conference_and_modules_path, get_gui_path


server = Flask(__name__, static_url_path='/static', static_folder=get_conference_and_modules_path(), template_folder=get_gui_path())
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1 

@dataclass
class Conference:
    modules: list[int]

conference_modules: list[ConferenceModule] = read_modules(get_conference_and_modules_path())
conference = Conference(modules=[])

@server.route('/')
def landing():
    """
    Render index.html. Initialization is performed asynchronously in initialize() function
    """
    return render_template('index.html', modules=conference_modules, conference=render_conference(get_current_conference()))


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

@server.route('/download', methods=['POST'])
def download():
    files = [os.path.join(get_assets_path(), "base.slides.pptx")] + [next(m.slides_path for m in conference_modules if m.id == id) for id in get_current_conference().modules]

    file = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_conference.pptx')
    if file and len(file) > 0:
        merge_presentations(files, file)

    return ''

def get_current_conference() -> Conference:
    return conference

def set_current_conference(c: Conference):
    global conference
    conference = c

def render_conference(c: Conference):
    modules: list[ConferenceModule] = [next(m for m in conference_modules if m.id == id) for id in c.modules]
    modules_data = [
        {
            "image_url": module.img_url,
            "title": module.title,
            "description": module.description,
            "duration_minutes": module.duration_minutes,
            # "tags_categories": [ { "category": k, "tags_details": list(v) } for k, v in groupby([{ "tag": cm.tag, "importance": math.floor(cm.tag_category_importance * 100) } for cm in ConferenceModuleTag.objects.order_by('tag__category').filter(conference_module=module.id).select_related('tag', 'tag__category')], lambda t:t["tag"].category.name) ],
            "tags_categories": [],
            "previous": idx -1,
            "next": idx + 1
        } for idx, module in enumerate(modules)
    ]
    total_duration = np.sum([module.duration_minutes for module in modules])

    # conference_module_tags = ConferenceModuleTag.objects.order_by('tag__category', 'tag__name').filter(conference_module__in=[module.id for module in modules]).select_related('tag', 'tag__category', 'conference_module')
    # tags_grouped_by_category = groupby([{ "tag": cm.tag, "duration_minutes": cm.tag_category_importance * cm.conference_module.duration_minutes } for cm in conference_module_tags], lambda t:t["tag"].category.name)
    # categories_tags_repartition = [ { "category": category, "tags": [{"tag": tag, "duration_minutes": np.sum([occ["duration_minutes"] for occ in tag_details])} for tag, tag_details in groupby(tags_details, lambda item: item["tag"].name)] } for category, tags_details in tags_grouped_by_category ]
    return render_template('conference.html', modules=modules_data, stats={
        "duration_minutes": total_duration,
        "categories_tags_repartition": []
    })

# @server.route('/choose/path', methods=['POST'])
# def choose_path():
#     """
#     Invoke a folder selection dialog here
#     :return:
#     """
#     dirs = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
#     if dirs and len(dirs) > 0:
#         directory = dirs[0]
#         if isinstance(directory, bytes):
#             directory = directory.decode('utf-8')

#         response = {'status': 'ok', 'directory': directory}
#     else:
#         response = {'status': 'cancel'}

#     return jsonify(response)


# @server.route('/fullscreen', methods=['POST'])
# def fullscreen():
#     webview.windows[0].toggle_fullscreen()
#     return jsonify({})


# @server.route('/open-url', methods=['POST'])
# def open_url():
#     url = request.json['url']
#     webbrowser.open_new_tab(url)

#     return jsonify({})


# @server.route('/do/stuff', methods=['POST'])
# def do_stuff():
#     response = {'status': 'ok', 'result': 'oki'}
#     return jsonify(response)