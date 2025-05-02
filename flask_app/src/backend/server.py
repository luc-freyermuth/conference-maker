import os
from dataclasses import dataclass
import numpy as np

from flask import Flask, render_template

from modules import ConferenceModule, read_modules

gui_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'gui')  # development path

conference_and_modules_dir = 'C:\\Users\\Luc\\Nextcloud Shifters\\TTS\\50 - TTS Contenus\\7. Modules'

if not os.path.exists(gui_dir):  # frozen executable path
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')

server = Flask(__name__, static_url_path='/static', static_folder=conference_and_modules_dir, template_folder=gui_dir)
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1 

@dataclass
class Conference:
    modules: list[int]

conference_modules: list[ConferenceModule] = read_modules(conference_and_modules_dir)
conference = Conference(modules=[1])

@server.route('/')
def landing():
    """
    Render index.html. Initialization is performed asynchronously in initialize() function
    """
    return render_template('index.html', modules=conference_modules, conference=render_conference(conference))


@server.route('/add-module/<int:module_id>', methods=['POST'])
def add_module(module_id):
    conference.modules.append(module_id)
    return render_conference(conference)


def render_conference(conference: Conference):
    modules: list[ConferenceModule] = [next(m for m in conference_modules if m.id == id) for id in conference.modules]
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


def read_modules(folder) -> list[ConferenceModule]:
    pass

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