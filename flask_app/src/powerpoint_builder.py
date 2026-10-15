import base64
import os

import aspose.slides as slides
from aspose.slides.export import SaveFormat

from config import get_assets_path
from modules import ConferenceModule
from conference import Conference, ModuleConferencePart, CoverSlideConferencePart


# Without a license, Aspose adds an evaluation watermark to generated slides.
# slides.License().set_license(os.environ['ASPOSESLIDES_LIC_PATH'])

SOURCES_SEPARATOR = '-----------------------------------------------------------------------------------------------------------------------------------'


def create_conference_slides(modules: list[ConferenceModule], conference: Conference, date: str, pptx_save_path: str | None = None, pdf_save_path: str | None = None):
  with slides.Presentation(os.path.join(get_assets_path(), "base.slides.pptx")) as prs:
    cover_slide = append_asset_slides(prs, "cover.slides.pptx")
    prs.sections.add_section('Couverture', cover_slide)

    cover_title_shape = next((shape for shape in cover_slide.shapes if (hasattr(shape, 'text_frame')) and len(shape.text_frame.paragraphs) > 0 and shape.text_frame.paragraphs[0].text == 'Titre'), None)
    if (cover_title_shape is None):
      raise ValueError('Unable to find text frame to put title, subtitle and date in cover slide')
    cover_title_shape.text_frame.paragraphs[0].text = conference.title
    cover_title_shape.text_frame.paragraphs[1].text = conference.subtitle
    cover_title_shape.text_frame.paragraphs[3].text = date

    for i, part in enumerate(conference.parts):
      if isinstance(part, ModuleConferencePart):
        module = next(m for m in modules if m.id == part.module_id)
        append_module_slides(prs, module, part.hide_cover_slide)
      if isinstance(part, CoverSlideConferencePart):
        transition_slide = append_asset_slides(prs, "cover_slide_part.slides.pptx")
        prs.sections.add_section(f'Transition: {part.title}', transition_slide)

        transition_slide.shapes[0].text_frame.text = part.title
        if part.image is not None:
          print(f'Adding picture to transition slide {transition_slide.slide_number}')
          fill_picture_placeholder(prs, transition_slide, base64.b64decode(part.image.base64))
        else:
          print(f'Transtion slide ({i}, {transition_slide.slide_number}) has no image. Skipping.')

    conclusion_slide = append_asset_slides(prs, "conclusion.slides.pptx")
    prs.sections.add_section('Conclusion & remerciements', conclusion_slide)

    if pptx_save_path is not None:
      print(f'Saving conference pptx to: {pptx_save_path}')
      prs.save(os.path.abspath(pptx_save_path), SaveFormat.PPTX)
      print(f'Saved conference pptx')
    if pdf_save_path is not None:
      print(f'Saving conference PDF to: {pdf_save_path}')
      prs.save(os.path.abspath(pdf_save_path), SaveFormat.PDF)
      print(f'Saved conference PDF')


def append_asset_slides(prs: slides.Presentation, asset_file_name: str) -> slides.ISlide:
  with slides.Presentation(os.path.join(get_assets_path(), asset_file_name)) as asset_prs:
    # Matches PowerPoint's InsertFromFile: slides take the design of the base presentation.
    appended_slides = [prs.slides.add_clone(asset_slide, prs.masters[0], True) for asset_slide in asset_prs.slides]
  return appended_slides[0]


def append_module_slides(prs: slides.Presentation, module: ConferenceModule, hide_cover_slide: bool):
  module_slides_path = os.path.abspath(module.slides_path)
  first_appended_slide: slides.ISlide | None = None

  with slides.Presentation(module_slides_path) as module_prs:
    for src_slide_index0, src_slide in enumerate(module_prs.slides):
      src_slide_index1 = src_slide_index0 + 1
      if src_slide_index1 == 1 and hide_cover_slide:
        print(f"skipping cover slide for ({ module.id }, { module.title })")
        continue

      # target layout is matched using layout ids (int prefixes in layout names)
      src_layout_id = extract_layout_id_from_layout_name(src_slide.layout_slide.name)
      if src_layout_id is None:
        raise ValueError(f'src layout has no id ({ module.id }, { module.title }, { src_slide_index1 }). You should use premade slide layouts for your conference.')
      print(f'slide {src_slide_index1} from pres {module_slides_path} layout_id : {src_layout_id}')
      target_layout = find_layout_slide_with_id(prs, src_layout_id)
      if target_layout is None:
        raise ValueError(f'no layout with id {src_layout_id} in base presentation ({ module.id }, { module.title }, { src_slide_index1 }).')

      target_slide = prs.slides.add_clone(src_slide, target_layout)
      if first_appended_slide is None:
        first_appended_slide = target_slide

      slide_sources = [source for source in module.sources if source.slide_index1 == src_slide_index1]
      if len(slide_sources) > 0:
        append_notes_lines(target_slide, [
          '',
          SOURCES_SEPARATOR,
          '',
          'Sources :',
          *[f'{slide_source.title} {f'({slide_source.value})' if slide_source.value else ''} : { slide_source.source }' for slide_source in slide_sources],
        ])

  if first_appended_slide is not None:
    prs.sections.add_section(f'{module.id} - {module.title}', first_appended_slide)


def append_notes_lines(slide: slides.ISlide, lines: list[str]):
  notes_slide = slide.notes_slide_manager.notes_slide or slide.notes_slide_manager.add_notes_slide()
  # Paragraphs are added one by one instead of rewriting the whole text, to keep the formatting of existing notes.
  for line in lines:
    paragraph = slides.Paragraph()
    paragraph.text = line
    notes_slide.notes_text_frame.paragraphs.add(paragraph)


def fill_picture_placeholder(prs: slides.Presentation, slide: slides.ISlide, image_bytes: bytes):
  picture_placeholder = next(
    (shape for shape in slide.shapes if shape.placeholder is not None and shape.placeholder.type == slides.PlaceholderType.PICTURE),
    None,
  )
  if picture_placeholder is None:
    raise ValueError(f'no picture placeholder found on slide {slide.slide_number}.')

  image = prs.images.add_image(image_bytes)

  # Filling the placeholder shape is not enough: PowerPoint still sees it as empty and shows its "insert picture" icon.
  # The placeholder is replaced by a picture frame linked to the same layout placeholder.
  picture_frame = slide.shapes.insert_picture_frame(
    slide.shapes.index_of(picture_placeholder),
    slides.ShapeType.RECTANGLE,
    picture_placeholder.x,
    picture_placeholder.y,
    picture_placeholder.width,
    picture_placeholder.height,
    image,
  )
  picture_frame.add_placeholder(picture_placeholder.placeholder)

  # Crop the image overflow equally on both sides, so the image is never distorted.
  picture_format = picture_frame.picture_format
  image_ratio = image.width / image.height
  placeholder_ratio = picture_placeholder.width / picture_placeholder.height
  if image_ratio > placeholder_ratio:
    horizontal_crop_percent = (1 - placeholder_ratio / image_ratio) / 2 * 100
    picture_format.crop_left = horizontal_crop_percent
    picture_format.crop_right = horizontal_crop_percent
  else:
    vertical_crop_percent = (1 - image_ratio / placeholder_ratio) / 2 * 100
    picture_format.crop_top = vertical_crop_percent
    picture_format.crop_bottom = vertical_crop_percent

  slide.shapes.remove(picture_placeholder)


def extract_layout_id_from_layout_name(layout_name: str) -> int | None:
  try:
    return int(layout_name.split('-')[0])
  except ValueError:
    return None


def find_layout_slide_with_id(prs: slides.Presentation, id: int) -> slides.ILayoutSlide | None:
  for master in prs.masters:
    for layout_slide in master.layout_slides:
      if extract_layout_id_from_layout_name(layout_slide.name) == id:
        return layout_slide
  return None
