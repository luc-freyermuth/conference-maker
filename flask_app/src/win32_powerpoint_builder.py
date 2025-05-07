import win32com.client
import os
import pythoncom

from config import get_assets_path
from modules import ConferenceModule

def create_conference_slides(modules: list[ConferenceModule], save_path: str):
  pythoncom.CoInitialize()
  ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
  prs = ppt_instance.Presentations.open(os.path.join(get_assets_path(), "base.slides.pptx"), True, False, False)

  r = prs.Slides.Count

  for i in range(len(modules)):
    prs_src =  ppt_instance.Presentations.open(os.path.abspath(modules[i].slides_path), True, False, False)
    prs.SectionProperties.AddSection(i + 1, f'{modules[i].id} - {modules[i].title}')
    prs.Slides.InsertFromFile(os.path.abspath(modules[i].slides_path), prs.Slides.Count)
    prs.Slides.Range(range(r + 1, r + 1 + prs_src.Slides.Count)).MoveToSectionStart(i+1)
    for s in range(1, prs_src.Slides.Count + 1):
      r = r + 1
      print(f'apply style of slide {s} from pres {os.path.abspath(modules[i].slides_path)} to slide {r}')
      prs.Slides.Item(r).Design = prs_src.Slides.Item(s).Design
    prs_src.Close()

  out = os.path.abspath(save_path)

  prs.SaveAs(out)
  prs.Close()