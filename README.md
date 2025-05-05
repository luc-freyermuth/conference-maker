# conference-maker

Run in dev :

```
uv run .\flask_app\src\main.py
```

Build exe :

```
uv run python -m PyInstaller .\flask_app\src\main.py -w -F --add-data "flask_app\gui;gui" --add-data "flask_app\assets;assets"
```