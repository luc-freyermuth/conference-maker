import sys
import os

assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')  # development path
if not os.path.exists(assets_dir):  # frozen executable path
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

gui_dir = os.path.join(os.path.dirname(__file__), '..', 'gui')  # development path
if not os.path.exists(gui_dir):  # frozen executable path
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')


if getattr(sys, 'frozen', False):
    print('frozen')
    application_path = os.path.dirname(sys.executable)
else:
    print('not frozen')
    application_path = os.path.dirname(__file__)

if os.path.exists(os.path.join(application_path, 'modules')):
    conference_and_modules_dir = application_path
elif os.environ.get('CONFERENCE_AND_MODULES_PATH') is not None:
    conference_and_modules_dir = os.environ.get('CONFERENCE_AND_MODULES_PATH')
else:
    raise RuntimeError('Enable to find conference and modules path')


print('assets dir: ' + assets_dir)
print('gui dir: ' + gui_dir)
print('conference_and_modules dir: ' + conference_and_modules_dir)

def is_dev_mode():
    return not getattr(sys, 'frozen', False)

def get_assets_path():
    return assets_dir

def get_gui_path():
    return gui_dir

def get_conference_and_modules_path():
    return conference_and_modules_dir