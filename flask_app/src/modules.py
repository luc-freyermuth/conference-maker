from dataclasses import dataclass
import os
import pandas as pd
from itertools import groupby
from pptx import Presentation

@dataclass
class ModuleTag:
    category: str
    tag: str

@dataclass
class TagCategory:
    name: str
    tags: list[ModuleTag]

@dataclass
class ModuleMessage:
    slide_index1: int
    content: str

@dataclass
class ConferenceModule:
    id: int
    title: str
    description: str
    duration_minutes: int
    img_url: str
    slides_path: str
    tags: list[ModuleTag]
    has_cover_slide: bool
    messages: list[ModuleMessage]
    slides_count: int


def read_modules(folder) -> list[ConferenceModule]:
    modules_folder = os.path.join(folder, 'modules')
    modules_subfolders = os.listdir(modules_folder)
    modules: list[ConferenceModule] = []
    for module_subfolder in modules_subfolders:
        module_path = os.path.join(modules_folder, module_subfolder)
        
        module_files = [f for f in os.listdir(module_path) if os.path.isfile(os.path.join(module_path, f))]

        module_definition_file = next(x for x in module_files if x.endswith('module.xlsx'))
        module_definition_file_path = os.path.join(module_path, module_definition_file)

        module_slides_file = next(x for x in module_files if x.endswith('slides.pptx'))
        module_slides_file_path = os.path.join(module_path, module_slides_file)

        prs = Presentation(module_slides_file_path)
        slides_count = len(prs.slides)

        pd_xl_file = pd.ExcelFile(module_definition_file_path)
        general_df = pd.read_excel(pd_xl_file, 'General', header=None)
        tags_df = pd.read_excel(pd_xl_file, 'Etiquettes')
        messages_df = pd.read_excel(pd_xl_file, 'Messages clés pour évaluation')

        module_cover_file = next((x for x in module_files if x.endswith('cover.png') or x.endswith('cover.jpg')), None)

        pd_xl_file.close()

        if general_df[1][4] != 'Caché':
            modules.append(ConferenceModule(
                id=int(module_subfolder[0:4]),
                title=general_df[1][0],
                description=general_df[1][1],
                duration_minutes=general_df[1][2],
                img_url=f'/static/modules/{module_subfolder}/{module_cover_file}' if module_cover_file is not None else '',
                slides_path=f'{modules_folder}/{module_subfolder}/{module_slides_file}',
                tags=[ModuleTag(category, tag) for category in tags_df.columns for tag in tags_df[category].tolist() if isinstance(tag, str)],
                has_cover_slide=general_df[1][3],
                messages=[ModuleMessage(row.iloc[0], row.iloc[1]) for _, row in messages_df.iterrows()],
                slides_count=slides_count
            ))

    return modules

def get_all_tags(modules: list[ConferenceModule]) -> list[TagCategory]:
    tags: list[ModuleTag] = []
    for module in modules:
        tags = tags + module.tags
    return  [TagCategory(name=k, tags=unique_by_key(v, lambda t: t.tag)) for k, v in groupby(sorted(tags, key=lambda m:m.category), lambda m:m.category)]


def unique_by_key(list, getkey):
    seen = set()
    return [seen.add(getkey(obj)) or obj for obj in list if getkey(obj) not in seen]