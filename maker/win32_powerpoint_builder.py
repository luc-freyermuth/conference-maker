import win32com.client
import os
from datetime import datetime

def merge_presentations(presentations, path):
  ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
  prs = ppt_instance.Presentations.open(os.path.abspath(presentations[0]), True, False, False)

  for i in range(1, len(presentations)):
    prs.Slides.InsertFromFile(os.path.abspath(presentations[i]), prs.Slides.Count)

  out = os.path.abspath(path)

  prs.SaveAs(out)
  prs.Close()
  return out