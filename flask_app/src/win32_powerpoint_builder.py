import win32com.client
import os
import pythoncom


def merge_presentations(presentations, path):
  pythoncom.CoInitialize()
  ppt_instance = win32com.client.Dispatch('PowerPoint.Application')
  print("Will merge presentations :")
  print(presentations, path)
  prs = ppt_instance.Presentations.open(os.path.abspath(presentations[0]), True, False, False)

  r = prs.Slides.Count

  for i in range(1, len(presentations)):
    prs_src =  ppt_instance.Presentations.open(os.path.abspath(presentations[i]), True, False, False)
    prs.Slides.InsertFromFile(os.path.abspath(presentations[i]), prs.Slides.Count)
    for s in range(1, prs_src.Slides.Count + 1):
      r = r + 1
      print(f'apply style of slide {s} from pres {os.path.abspath(presentations[i])} to slide {r}')
      prs.Slides.Item(r).Design = prs_src.Slides.Item(s).Design
    prs_src.Close()

  out = os.path.abspath(path)

  prs.SaveAs(out)
  prs.Close()
  return out
