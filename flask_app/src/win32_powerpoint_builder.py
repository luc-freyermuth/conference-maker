import win32com.client
import os
import pythoncom

from config import get_assets_path
from modules import ConferenceModule
from conference import Conference, ModuleConferencePart, CoverSlideConferencePart

def create_conference_slides(modules: list[ConferenceModule], conference: Conference, date: str, save_path: str):
  pythoncom.CoInitialize()
  ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
  prs = ppt_instance.Presentations.open(os.path.join(get_assets_path(), "base.slides.pptx"), True, False, False)

  prs.SectionProperties.AddSection(1, f'Couverture')
  prs.Slides.InsertFromFile(os.path.join(get_assets_path(), "cover.slides.pptx"), prs.Slides.Count)
  prs.Slides.Range(1).MoveToSectionStart(1)

  prs.Slides(1).Shapes(prs.Slides(1).Shapes.Count).TextFrame.TextRange.Paragraphs(1).Text = conference.title
  prs.Slides(1).Shapes(prs.Slides(1).Shapes.Count).TextFrame.TextRange.Paragraphs(2).Text = conference.subtitle
  prs.Slides(1).Shapes(prs.Slides(1).Shapes.Count).TextFrame.TextRange.Paragraphs(4).Text = date

  current_slide_target = prs.Slides.Count

  for i in range(len(conference.parts)):
    part = conference.parts[i]
    if isinstance(part, ModuleConferencePart):
      module = next(m for m in modules if m.id == part.module_id)
      prs_src =  ppt_instance.Presentations.open(os.path.abspath(module.slides_path), True, False, False)
      prs.SectionProperties.AddSection(i + 2, f'{module.id} - {module.title}')
      prs.Slides.InsertFromFile(os.path.abspath(module.slides_path), prs.Slides.Count)
      prs.Slides.Range(range(current_slide_target + 1, current_slide_target + 1 + prs_src.Slides.Count)).MoveToSectionStart(i+2)
      
      for current_slide_src in range(1, prs_src.Slides.Count + 1):
        if current_slide_src == 1 and part.hide_cover_slide:
          print(f"skipping cover slide for ({ module.id }, { module.title })")
          prs.Slides.Item(current_slide_target + 1).Delete()
          continue
        current_slide_target = current_slide_target + 1
        src_layout_id = extract_layout_id_from_layout_name(prs_src.Slides.Item(current_slide_src).CustomLayout.Name)
        if src_layout_id is None:
          raise ValueError(f'src layout has no id ({ module.id }, { module.title }, { current_slide_src }). You should use premade slide layouts for your conference.')
        print(f'slide {current_slide_src} from pres {os.path.abspath(module.slides_path)} layout_id : {src_layout_id}')
        target_layout = find_custom_layout_with_id(prs, src_layout_id)
        prs.Slides.Item(current_slide_target).CustomLayout = target_layout
      prs_src.Close()
    if isinstance(part, CoverSlideConferencePart):
      current_slide_target = current_slide_target + 1
      prs.SectionProperties.AddSection(i + 2, f'Transition: {part.title}')
      prs.Slides.InsertFromFile(os.path.join(get_assets_path(), "cover_slide_part.slides.pptx"), prs.Slides.Count)
      prs.Slides(current_slide_target).MoveToSectionStart(i+2)

      prs.Slides(current_slide_target).Shapes(1).TextFrame.TextRange.Text = part.title
      prs.Slides(current_slide_target).Shapes.AddPicture(f'http://localhost:5000/dynamic-assets/current-conference/cover-slide-part/image/{i}',False, True, 0 ,0 , -1 , -1 )

  prs.SectionProperties.AddSection(len(conference.parts) + 2, f'Conclusion & remerciements')
  prs.Slides.InsertFromFile(os.path.join(get_assets_path(), "conclusion.slides.pptx"), prs.Slides.Count)
  prs.Slides.Range(current_slide_target + 1).MoveToSectionStart(len(conference.parts) + 2)

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
