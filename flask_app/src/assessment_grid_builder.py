from modules import ConferenceModule
from conference import Conference, ModuleConferencePart

from openpyxl import Workbook
from openpyxl.styles.borders import Border, Side, BORDER_MEDIUM
from openpyxl.styles.fonts import Font
from openpyxl.styles.alignment import Alignment

bottom_border = Border(bottom=Side(border_style=BORDER_MEDIUM))


def create_assessment_grid(modules: list[ConferenceModule], conference: Conference, save_path: str):
    wb = Workbook()
    ws = wb.active
    ws.append(["Module", "Slide", "Messages clés / Critères", "Commentaires"])
    curr_row = 1
    for part in conference.parts:
        if isinstance(part, ModuleConferencePart):
            module = next(m for m in modules if m.id == part.module_id)
            for message in module.messages:
                ws.append([module.title, message.slide_index1, message.content])
                curr_row += 1
            ws.append([module.title, 'TODO', f'Respect du timing : environ {module.duration_minutes} minute{'s' if module.duration_minutes > 1 else ''}'])
            curr_row += 1
            for i in range(4):
                ws.cell(row=curr_row, column=i+1).border = bottom_border
        else:
            pass
    ws.column_dimensions['A'].width = 31
    ws.column_dimensions['B'].width = 8
    ws.column_dimensions['C'].width = 72
    ws.column_dimensions['D'].width = 50
    # TODO
    ws.column_dimensions['C'].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[1].font = Font(bold=True)
    
    wb.save(save_path)