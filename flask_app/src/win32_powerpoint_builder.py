import win32com.client
import os
import pythoncom

from config import get_assets_path
from modules import ConferenceModule
from conference import Conference, ModuleConferencePart, CoverSlideConferencePart
from image_cache import image_cache
from typing import Any


def create_conference_slides(modules: list[ConferenceModule], conference: Conference, date: str, pptx_save_path: str | None = None, pdf_save_path: str | None = None):
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

        # set layout in target prs using layout ids (int prefixes in layout names)
        src_layout_id = extract_layout_id_from_layout_name(prs_src.Slides.Item(current_slide_src).CustomLayout.Name)
        if src_layout_id is None:
          raise ValueError(f'src layout has no id ({ module.id }, { module.title }, { current_slide_src }). You should use premade slide layouts for your conference.')
        print(f'slide {current_slide_src} from pres {os.path.abspath(module.slides_path)} layout_id : {src_layout_id}')
        target_layout = find_custom_layout_with_id(prs, src_layout_id)
        prs.Slides.Item(current_slide_target).CustomLayout = target_layout

        # add sources at the bottom of slides notes
        slide_sources = [source for source in module.sources if source.slide_index1 == current_slide_src]
        if len(slide_sources) > 0:
          notes_text_frame: Any = None
          for shape_index in range(1, prs.Slides.Item(current_slide_target).NotesPage.Shapes.Count + 1):
            if prs.Slides.Item(current_slide_target).NotesPage.Shapes(shape_index).PlaceholderFormat.Type == 2:
              notes_text_frame = prs.Slides.Item(current_slide_target).NotesPage.Shapes(shape_index)
          notes_text_frame.TextFrame.TextRange.InsertAfter("\n\n-----------------------------------------------------------------------------------------------------------------------------------\n\nSources :\n")
          for slide_source in slide_sources:
            notes_text_frame.TextFrame.TextRange.InsertAfter(f'{slide_source.title} {f'({slide_source.value})' if slide_source.value else ''} : { slide_source.source }\n')
      prs_src.Close()
    if isinstance(part, CoverSlideConferencePart):
      current_slide_target = current_slide_target + 1
      prs.SectionProperties.AddSection(i + 2, f'Transition: {part.title}')
      prs.Slides.InsertFromFile(os.path.join(get_assets_path(), "cover_slide_part.slides.pptx"), prs.Slides.Count)
      prs.Slides(current_slide_target).MoveToSectionStart(i+2)

      prs.Slides(current_slide_target).Shapes(1).TextFrame.TextRange.Text = part.title
      if (part.image is not None):
        cache_id = image_cache.add_to_cache(part.image.base64)
        picture_url = f'http://localhost:5000/dynamic-assets/image_cache/{cache_id}'
        print(f'Adding picture {picture_url} to transition slide {current_slide_target}')
        prs.Slides(current_slide_target).Shapes.AddPicture(picture_url, False, True, 0, 0, -1, -1)
      else:
        print(f'Transtion slide ({i}, {current_slide_target}) has no image. Skipping.')

  prs.SectionProperties.AddSection(len(conference.parts) + 2, f'Conclusion & remerciements')
  prs.Slides.InsertFromFile(os.path.join(get_assets_path(), "conclusion.slides.pptx"), prs.Slides.Count)
  prs.Slides.Range(current_slide_target + 1).MoveToSectionStart(len(conference.parts) + 2)

  if pptx_save_path is not None:
    out_pptx = os.path.abspath(pptx_save_path)
    print(f'Saving conference pptx to: {pptx_save_path}')
    prs.SaveAs(out_pptx)
    print(f'Saved conference pptx')
  if pdf_save_path is not None:
    out_pdf = os.path.abspath(pdf_save_path)
    print(f'Saving conference PDF to: {pdf_save_path}')
    prs.ExportAsFixedFormat(out_pdf, 2, PrintRange=None)
    print(f'Saved conference PDF')
  prs.Close()
  image_cache.clear_cache()


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
