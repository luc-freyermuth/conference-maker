from dataclasses import dataclass
import os
import pandas as pd
import urllib.parse as urlparse
import urllib.request as urlrequest

@dataclass
class ConferenceModule:
    id: int
    title: str
    description: str
    duration_minutes: int
    img_url: str
    slides_path: str

def read_modules(folder) -> list[ConferenceModule]:
    modules_folder = os.path.join(folder, 'modules')
    modules_subfolders = os.listdir(modules_folder)
    modules: list[ConferenceModule] = []
    for module_subfolder in modules_subfolders:
        module_path = os.path.join(modules_folder, module_subfolder)
        
        module_files = [f for f in os.listdir(module_path) if os.path.isfile(os.path.join(module_path, f))]
        module_definition_file = next(x for x in module_files if x.endswith('module.xlsx'))
        module_definition_file_path = os.path.join(module_path, module_definition_file)

        pd_xl_file = pd.ExcelFile(module_definition_file_path)
        general_df = pd.read_excel(pd_xl_file, 0, header=None)

        module_cover_file = next((x for x in module_files if x.endswith('cover.png') or x.endswith('cover.jpg')), None)

        slides_file = next((x for x in module_files if x.endswith('slides.pptx')), None)

        if general_df[1][3] != 'Caché':
            modules.append(ConferenceModule(
                id=int(module_subfolder[0:4]),
                title=general_df[1][0],
                description=general_df[1][1],
                duration_minutes=general_df[1][2],
                img_url=f'/static/modules/{module_subfolder}/{module_cover_file}' if module_cover_file is not None else '',
                slides_path=f'{modules_folder}/{module_subfolder}/{slides_file}'
            ))

    return modules