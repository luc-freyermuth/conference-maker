from modules import ConferenceModule, ModuleMessage
from conference import Conference, ModuleConferencePart

from openpyxl import Workbook
from openpyxl.styles.borders import Border, Side, BORDER_MEDIUM
from openpyxl.styles.fonts import Font
from openpyxl.styles.alignment import Alignment
from openpyxl.styles.fills import PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

status_validation = DataValidation(type="list", formula1='"A renseigner,Pas abordé,Incomplet,Parfait"', allow_blank=True)

def create_assessment_grid(modules: list[ConferenceModule], conference: Conference, save_path: str):
    wb = Workbook()
    ws = wb.active
    ws.add_data_validation(status_validation)
    ws.append(["Module", "Slide", "Statut", "Messages clés / Critères", "Commentaires"])
    curr_row = 1
    curr_slides = 1
    for part in conference.parts:
        if isinstance(part, ModuleConferencePart):
            module = next(m for m in modules if m.id == part.module_id)
            slides_count = module.slides_count if part.hide_cover_slide is False else module.slides_count - 1
            messages = [
                ModuleMessage(
                    slide_index1=m.slide_index1 if part.hide_cover_slide is False else max(m.slide_index1 - 1, 1), 
                    content=m.content
                ) for m in module.messages
            ]
            for message in messages:
                ws.append([module.title, message.slide_index1 + curr_slides, 'A renseigner', message.content])
                curr_row += 1
                status_validation.add(ws.cell(row=curr_row, column=3))
            ws.append([
                module.title, 
                f'{curr_slides + 1} à {curr_slides + slides_count}' if slides_count > 1 else curr_slides + 1, 
                'A renseigner',
                f'Respect du timing : environ {module.duration_minutes} minute{'s' if module.duration_minutes > 1 else ''}'
            ])
            curr_row += 1
            status_validation.add(ws.cell(row=curr_row, column=3))
            for i in range(5):
                ws.cell(row=curr_row, column=i+1).border = Border(bottom=Side(border_style=BORDER_MEDIUM))
                ws.cell(row=curr_row, column=i+1).fill = PatternFill("solid", fgColor="F2F2F2")
            curr_slides += slides_count
        else:
            curr_slides += 1
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 8
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 80
    ws.column_dimensions['E'].width = 50

    for i in range(5):
        ws.cell(row=1, column=i+1).font = Font(bold=True)

    for i in range(curr_row):
        ws.cell(row=i+1, column=1).alignment = Alignment(vertical='center', wrap_text=True)
        ws.cell(row=i+1, column=2).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=i+1, column=3).alignment = Alignment(vertical='center')
        ws.cell(row=i+1, column=4).alignment = Alignment(vertical='center', wrap_text=True)
    
    wb.save(save_path)