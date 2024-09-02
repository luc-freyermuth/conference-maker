import win32com.client
import os
from datetime import datetime

work_dir = "C:/Users/Luc/Documents/conference-maker"

path0=f"assets/Base.pptx"
path1=f"modules_files/GP_1.pptx"
path2=f"modules_files/EE_2.pptx"
path3=f"modules_files/LY_1.pptx"
lst=[path0, path1,path2,path3]
output_path=f"out/out_{datetime.now().strftime('%m_%d_%Y %H_%M_%S')}.pptx" 

def merge_presentations(presentations, path):
  ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
  prs = ppt_instance.Presentations.open(os.path.abspath(presentations[0]), True, False, False)

  for i in range(1, len(presentations)):
    prs.Slides.InsertFromFile(os.path.abspath(presentations[i]), prs.Slides.Count)

  prs.SaveAs(os.path.abspath(path))
  prs.Close()

merge_presentations(lst,output_path)