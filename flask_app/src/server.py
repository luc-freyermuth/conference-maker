from itertools import groupby
import numpy as np
from datetime import datetime
from typing import Tuple, cast, Any
import os

from flask import Flask, render_template, request, send_from_directory, send_file

from modules import ConferenceModule, read_modules, get_all_tags
from win32_powerpoint_builder import create_conference_slides
from assessment_grid_builder import create_assessment_grid
import webview
from config import get_conference_and_modules_path, get_gui_path, get_assets_path
from conference import Conference, serialize_conference, deserialize_conference, ModuleConferencePart, CoverSlideConferencePart, CoverSlideConferencePartImage
import base64
import io
from image_cache import image_cache
import json



server = Flask(__name__, static_url_path='/static', static_folder=get_conference_and_modules_path(), template_folder=get_gui_path())
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

conference_modules: list[ConferenceModule] = read_modules(get_conference_and_modules_path())
conference = Conference(title='Ma conférence', subtitle='Accroche', parts=[])

@server.route('/')
def landing():
    return render_template('index.html', 
                           modules_list=render_modules_list(conference_modules), 
                           conference=render_conference(get_current_conference()), 
                           tags_categories=get_all_tags(conference_modules))


@server.route('/add-module/<int:module_id>', methods=['POST'])
def add_module(module_id: int):
    c = get_current_conference()
    c.parts.append(ModuleConferencePart(module_id=module_id, hide_cover_slide=False))
    set_current_conference(c)
    return render_conference(c)

@server.route('/add-cover-slide-part', methods=['POST'])
def add_cover_slide_part() -> str:
    c = get_current_conference()
    c.parts.append(CoverSlideConferencePart(title="Transition", image=None))
    set_current_conference(c)
    return render_conference(c)

@server.route('/move/<int:part_index>/<int:new_index>', methods=['POST'])
def move_module(part_index: int, new_index: int):
    c = get_current_conference()
    c.parts[part_index], c.parts[new_index] = c.parts[new_index], c.parts[part_index]
    set_current_conference(c)
    return render_conference(c)

@server.route('/part/<int:module_index>', methods=['DELETE'])
def remove_module(module_index: int):
    c = get_current_conference()
    c.parts.pop(module_index)
    set_current_conference(c)
    return render_conference(c)

@server.route('/reset', methods=['POST'])
def reset():
    new_conference = Conference(title='Ma conférence', subtitle='Accroche', parts=[])
    set_current_conference(new_conference)
    return render_conference(new_conference)

@server.route('/conference-settings', methods=['PUT'])
def set_conference_settings() -> str:
    c = get_current_conference()
    c.title = request.form.get("title") or ''
    c.subtitle = request.form.get("subtitle") or ''
    set_current_conference(c)
    return render_template('conference_settings.html', conference_title=c.title, conference_subtitle=c.subtitle)

@server.route('/cover-slide-part/<int:part_index>/title', methods=['PUT'])
def set_cover_slide_part_title(part_index: int):
    c = get_current_conference()
    part_to_edit = c.parts[part_index]
    if (not isinstance(part_to_edit, CoverSlideConferencePart)):
        raise ValueError('Part is not a cover slide')
    part_to_edit.title = request.form.get("title") or ''
    c.parts[part_index] = part_to_edit
    set_current_conference(c)
    return render_cover_slide_conference_part(part_to_edit, index=part_index, total=len(c.parts))

@server.route('/cover-slide-part/<int:part_index>/pick-image', methods=['POST'])
def cover_slide_part_pick_image(part_index: int):
    c = get_current_conference()
    part_to_edit = c.parts[part_index]
    if (not isinstance(part_to_edit, CoverSlideConferencePart)):
        raise ValueError('Part is not a cover slide')
    
    files = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG)
    if files and len(files) > 0:
        filename = files[0]
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')
        if not (filename.endswith('.jpg') or filename.endswith('.png')):
            raise ValueError('file is not an image')
        with open(filename, 'rb') as file:
            base64_bytes = base64.b64encode(file.read())
            base64_string = base64_bytes.decode()
            part_to_edit.image = CoverSlideConferencePartImage(base64=base64_string)
            c.parts[part_index] = part_to_edit
            set_current_conference(c)
    return render_cover_slide_conference_part(part_to_edit, index=part_index, total=len(c.parts))

@server.route('/module-part/<int:part_index>/hide-cover-slide', methods=['PUT'])
def set_module_part_hide_cover_slide(part_index: int):
    c = get_current_conference()
    part_to_edit = c.parts[part_index]
    if (not isinstance(part_to_edit, ModuleConferencePart)):
        raise ValueError('Part is not a module')
    part_to_edit.hide_cover_slide = request.form.get("hide-cover-slide") == 'on'
    c.parts[part_index] = part_to_edit
    set_current_conference(c)
    return render_module_conference_part(part_to_edit, get_module_by_id(part_to_edit.module_id), index=part_index, total=len(c.parts))

@server.route('/download', methods=['POST'])
def download():
    c = get_current_conference()

    file = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_conference.pptx')
    if file and len(file) > 0:
        create_conference_slides(
            conference_modules, 
            conference=c, 
            date=datetime.now().strftime("%d/%m/%Y"), 
            pptx_save_path=file
        )

    return ''

@server.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    c = get_current_conference()

    file = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_conference.pdf')
    if file and len(file) > 0:
        create_conference_slides(
            conference_modules, 
            conference=c, 
            date=datetime.now().strftime("%d/%m/%Y"), 
            pdf_save_path=file
        )

    return ''

@server.route('/generate-grid', methods=['POST'])
def generate_grid() -> str:
    c = get_current_conference()

    file = cast(str, webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_grille_d_evaluation.xlsx'))
    if file and len(file) > 0:
        create_assessment_grid(
            conference_modules, 
            conference=c, 
            save_path=file
        )

    return ''

@server.route('/export', methods=['POST'])
def export():
    serialized = serialize_conference(get_current_conference())
    file = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='ma_conference.focon')
    with open(file, "w") as text_file:
        text_file.write(serialized)
    return render_oob_toast('Fichier focon enregistré avec succès !')

@server.route('/import', methods=['POST'])
def import_conference():
    files = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, directory=get_conference_and_modules_path())
    if files and len(files) > 0:
        filename = files[0]
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')
        with open(filename) as file:
            set_current_conference(deserialize_conference(file.read()))
    return render_conference(get_current_conference())

@server.route('/generate-kit', methods=['POST'])
def generate_kit() -> Any:
    dirs = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG, directory=get_conference_and_modules_path())
    if not (dirs and len(dirs) > 0):
        return "Did not pick a conference directory", 400
    source_dir = dirs[0]
    if isinstance(source_dir, bytes):
        source_dir = source_dir.decode('utf-8')
    print(f'Will generate kit from directory: {source_dir}')

    kit_destination: str = cast(str, webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename='mon_kit'))

    if not kit_destination:
        return "Did not pick a destination", 400

    (kit_dir, kit_name) = os.path.split(kit_destination)
    print(f'Will generate kit with name "{kit_name}" in directory: {kit_dir}')

    if os.path.isdir(kit_destination):
        return "Kit already exists", 400

    files_in_src = [f for f in os.listdir(source_dir) if (os.path.isfile(os.path.join(source_dir, f)))]
    print(f'Files found in kit source directory: {files_in_src}')
    focon_files = [f for f in files_in_src if f.endswith('.focon')]
    print(f'Kit will be generated for focon files: {focon_files}')

    print(f'Creating kit directory: {kit_destination}')
    os.makedirs(kit_destination)

    for focon_file in focon_files:
        conference_name = focon_file.split('.')[0]
        focon_file_path = os.path.join(source_dir, focon_file)
        print(f'=== Generating files for focon_file: {focon_file_path} ===')
        conference: Conference
        with open(focon_file_path) as file:
            conference = deserialize_conference(file.read())
        print('Generating conference')
        create_conference_slides(
            conference_modules, 
            conference=conference, 
            date=datetime.now().strftime("%d/%m/%Y"), 
            pptx_save_path=os.path.join(kit_destination, f'{conference_name}_{datetime.now().strftime("%Y.%m")}.pptx'),
            pdf_save_path=os.path.join(kit_destination, f'{conference_name}_{datetime.now().strftime("%Y.%m")}.pdf'),
        )
        print('Generating assessement grid')
        create_assessment_grid(
            conference_modules, 
            conference=conference, 
            save_path=os.path.join(kit_destination, f'{conference_name}_{datetime.now().strftime("%Y.%m")}_Grille_d_evaluation.xlsx')
        )
        print(f'=== Files generated successfully for focon_file: {focon_file_path} ===')

    print('Kit generated successfully')
    return '', 204

@server.route('/search-modules', methods=['GET'])
def search_modules():
    search = request.args.get("search")
    tags = [(category_key.split('__')[1], request.args.get(category_key)) for category_key in filter(lambda k: k.startswith('category__') and request.args.get(k) != '', request.args.keys())]
    return render_modules_list(conference_modules, search, tags)


def get_current_conference() -> Conference:
    return conference

def set_current_conference(c: Conference):
    global conference
    conference = c

def render_modules_list(modules: list[ConferenceModule], search: str | None = None, tags: list[Tuple[str, str]] | None = None):
    if search:
        search = search.lower()
        modules = list(filter(lambda module: search in module.title.lower() or search in module.description.lower(), modules))
    if tags:
        for tag in tags:
            modules = list(filter(lambda module: len(list(filter(lambda t:t.category == tag[0] and t.tag == tag[1], module.tags))), modules))
    modules = list(modules)
    modules.sort(key=lambda m: m.title)
    return render_template('modules_list.html', modules=modules)

def render_conference(c: Conference):
    # modules: list[ConferenceModule] = [next(m for m in conference_modules if m.id == id) for id in c.modules]
    parts = [
        render_module_conference_part(part, get_module_by_id(part.module_id), idx, len(c.parts)) if isinstance(part, ModuleConferencePart) else render_cover_slide_conference_part(part, idx, len(c.parts))
        for idx, part in enumerate(c.parts)
    ]
    total_duration = sum([get_module_by_id(cast(ModuleConferencePart, part).module_id).duration_minutes for part in filter(lambda p: isinstance(p, ModuleConferencePart), c.parts)])


    modules_parts = [part for part in c.parts if isinstance(part, ModuleConferencePart)]
    modules = [get_module_by_id(part.module_id) for part in modules_parts]
    tags_with_duration = []
    for module in modules:
        for tag in module.tags:
            tags_with_duration.append({ "category": tag.category, "tag": tag.tag, "duration": module.duration_minutes })
    tags_with_duration.sort(key=lambda x:x["tag"])
    tags_with_duration.sort(key=lambda x:x["category"])
        
    by_category = [ { "category": k, "tags": [{ "name": k1, "duration": sum([t.get("duration") for t in v1]) } for k1, v1 in groupby(v, lambda t:t.get("tag"))] } for k, v in groupby(tags_with_duration, lambda t:t.get("category")) ]
    
    chart_configs = []
    for category in by_category:
        chart_config = {
                "type":"bar",
                "data": {
                    "labels":[],
                    "datasets":[{"label":"Minutes","data":[]}]
                },
                "options":{
                    "responsive":True, 
                    "maintainAspectRatio": False,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": category["category"]
                        },
                        "legend": {
                            "display": False
                        }
                    },
                    "scales": {
                        "y": {
                            "title": {
                                "display": True,
                                "text": "Minutes"
                            }
                        },
                        "x": {
                            "ticks": {
                                "display": len(category["tags"]) < 8,
                                "maxRotation": 90,
                                "minRotation": 0
                            }
                        }
                    }
                }
            }
        
        tags: list[dict] = category["tags"]
        tags.sort(key=lambda t:t["duration"])
        tags.reverse()
        chart_config["data"]["labels"] = [tag["name"] for tag in tags]
        chart_config["data"]["datasets"][0]["data"] = [tag["duration"] for tag in tags]
        chart_configs.append(chart_config)
    
    return render_template('conference.html', conference_title=c.title, conference_subtitle=c.subtitle, parts=parts, stats={
        "duration_minutes": total_duration,
        "categories_tags_repartition": [],
    }, chart_configs=[json.dumps(chart_config) for chart_config in chart_configs])

def render_module_conference_part(cp: ModuleConferencePart, module: ConferenceModule, index: int, total: int) -> str:
    return render_template('module_conference_part.html', 
                            image_url = module.img_url,
                            title = module.title,
                            description = module.description,
                            duration_minutes = module.duration_minutes,
                            tags_categories = [ { "category": k, "tags": [tag.tag for tag in v] } for k, v in groupby(module.tags, lambda t:t.category) ],
                            index = index,
                            is_first = index == 0,
                            is_last = index == (total - 1),
                            show_hide_cover = module.has_cover_slide,
                            hide_cover = cp.hide_cover_slide)

def render_cover_slide_conference_part(cp: CoverSlideConferencePart, index: int, total: int) -> str:
    return render_template('cover_slide_conference_part.html',
                           title = cp.title,
                           index = index,
                           image_url = f'data:image/png;base64,{cp.image.base64}' if cp.image else None,
                           is_first = index == 0,
                           is_last = index == (total - 1))

def get_module_by_id(module_id: int) -> ConferenceModule:
    module = next(m for m in conference_modules if m.id == module_id)
    if module is None:
        raise ValueError(f'module with id {module_id} not found')
    return module

toast_id = 0

def render_oob_toast(message: str) -> str:
    global toast_id
    toast_id += 1
    return render_template('toast.html', message=message, toast_id=toast_id)

@server.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory(get_assets_path(), filename)
    
@server.route('/dynamic-assets/image_cache/<int:cache_id>')
def dynamic_assets_from_cache(cache_id: int):
    base64_image = image_cache.get_from_cache(cache_id)
    b = base64.b64decode(base64_image.encode('utf-8'))
    buf = io.BytesIO(b)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")