# Starlette Admin Fields Example - Kitchensink

## Clone the repo

```shell
git clone https://github.com/hasansezertasan/starlette-admin-fields.git
cd starlette-admin-fields
```

## Install dependencies with virtualenv

- Create a virtual environment:

```shell
python3 -m venv venv
```

- Activate the virtual environment:

> On Windows:

```shell
venv/Scripts/activate.bat
```

> On Unix or MacOS:

```shell
source venv/bin/activate
```

- Install requirements:

```shell
pip install -r 'example/requirements.txt'
```

> To install current version of `starlette-admin-fields`, run `pip install -e .`.

## Run the application

```shell
uvicorn example.main:app
```
