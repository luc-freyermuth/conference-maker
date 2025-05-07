# conference-maker

Run in dev :

```
uv run .\flask_app\src\main.py
```

Build exe :

```sh
# for release
uv run python -m PyInstaller conference_builder.spec
```

Command used to generate spec file :

```sh
# for release
uv run python -m PyInstaller .\flask_app\src\main.py -w -F --add-data "flask_app\gui;gui" --add-data "flask_app\assets;assets" --name conference_builder

# with debug console for testing, spec file will be ignored by git
uv run python -m PyInstaller .\flask_app\src\main.py -w -F --add-data "flask_app\gui;gui" --add-data "flask_app\assets;assets" --name conference_builder_debug --console
```