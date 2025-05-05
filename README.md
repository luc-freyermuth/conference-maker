# conference-maker

Build flask app :

```
python -m PyInstaller .\flask_app\src\main.py -w -F --add-data "flask_app\gui;gui" --add-data "flask_app\assets;assets"
```