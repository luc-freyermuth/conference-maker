from typing import Tuple
import win32com.client
import os
import pythoncom

from config import get_assets_path
from modules import ConferenceModule

def create_conference_slides(modules: list[ConferenceModule], save_path: str):
  pythoncom.CoInitialize()
  ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
  prs = ppt_instance.Presentations.open(os.path.join(get_assets_path(), "base.slides.pptx"), True, False, False)

  current_slide_target = prs.Slides.Count

  for i in range(len(modules)):
    prs_src =  ppt_instance.Presentations.open(os.path.abspath(modules[i].slides_path), True, False, False)
    prs.SectionProperties.AddSection(i + 1, f'{modules[i].id} - {modules[i].title}')
    prs.Slides.InsertFromFile(os.path.abspath(modules[i].slides_path), prs.Slides.Count)
    prs.Slides.Range(range(current_slide_target + 1, current_slide_target + 1 + prs_src.Slides.Count)).MoveToSectionStart(i+1)
    
    for current_slide_src in range(1, prs_src.Slides.Count + 1):
      current_slide_target = current_slide_target + 1
      src_layout_id = extract_layout_id_from_layout_name(prs_src.Slides.Item(current_slide_src).CustomLayout.Name)
      print(f'slide {current_slide_src} from pres {os.path.abspath(modules[i].slides_path)} layout_id : {src_layout_id}')
      target_layout = find_custom_layout_with_id(prs, src_layout_id)
      prs.Slides.Item(current_slide_target).CustomLayout = target_layout
      # print(f'set slide {current_slide_target} to existing layout {target_layout.Name}')
    prs_src.Close()

  out = os.path.abspath(save_path)

  prs.SaveAs(out)
  prs.Close()

def extract_layout_id_from_layout_name(layout_name: str) -> int | None:
  try:
    return int(layout_name.split('-')[0])
  except ValueError:
    return None
  

def find_custom_layout_with_id(prs, id: int):
  for d in range(1, prs.Designs.Count + 1):
    for s in range(1, prs.Designs(d).SlideMaster.CustomLayouts.Count + 1):
      if (extract_layout_id_from_layout_name(prs.Designs(d).SlideMaster.CustomLayouts(s).Name) == id):
        return prs.Designs(d).SlideMaster.CustomLayouts(s)    
  return None
