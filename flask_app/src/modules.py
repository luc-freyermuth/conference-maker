from dataclasses import dataclass
import os
import pandas as pd
from itertools import groupby
from pptx import Presentation
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import date
import threading
from utils import debounce
import logging

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
class ModuleSource:
    slide_index1: int
    title: str
    value: str | None
    source: str
    expiry_date: date | None

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
    sources: list[ModuleSource]
    slides_count: int

class ConferenceModulesService:
    modules: list[ConferenceModule]
    conferences_and_modules_path: str

    def __init__(self, conferences_and_modules_path: str):
        self.modules = read_modules(conferences_and_modules_path)
        self.conferences_and_modules_path = conferences_and_modules_path
        threading.Thread(target=lambda: self._udpate_modules_regularly()).start()
        

    def get_modules(self) -> list[ConferenceModule]: 
        return self.modules
    
    def _udpate_modules_regularly(self):

        @debounce(5)
        def debouced_modules_update():
            logging.info('File change detected, updating modules...')
            self.modules = read_modules(self.conferences_and_modules_path)
            logging.info('Modules updated !')

        class UpdateModulesHandler(FileSystemEventHandler):
            def on_any_event(self, _):
                debouced_modules_update()

        observer = Observer()
        observer.schedule(UpdateModulesHandler(), os.path.join(self.conferences_and_modules_path, 'modules'), recursive=True)
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()


    

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
        sources_df = pd.read_excel(pd_xl_file, 'Données & sources')

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
                sources=[ModuleSource(
                    slide_index1=row.iloc[0], 
                    title=row.iloc[1], 
                    value=row.iloc[2] if not pd.isna(row.iloc[2]) else None, 
                    source=row.iloc[3], 
                    expiry_date=row.iloc[4].date() if not pd.isna(row.iloc[4]) else None
                ) for _, row in sources_df.iterrows()],
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