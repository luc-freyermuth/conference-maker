# conference-maker

## Run in dev :

#### Create .env file

```
cp template.env .env
```


#### Run using uv

```
uv run --env-file .env .\flask_app\src\main.py
```

## Build exe :

```sh
# for release
uv run python -m PyInstaller conference_builder_web.spec
```

#### Command used to generate spec file :

```sh
# for release
uv run python -m PyInstaller .\flask_app\src\main.py -w -F --add-data "flask_app\gui;gui" --add-data "flask_app\assets;assets" --name conference_builder_web --console
```