links
=====

[links][] collected by [narf][]

  [links]:  https://links.narf.pl/
  [narf]:   https://narf.pl/


### Deployment

This app runs on [Render](https://render.com).

#### build command

    pip install -r requirements.txt && PYTHONPATH=.:$PYTHONPATH python app/generator.py

#### start command

    gunicorn app.server:app --workers=2

#### Python version

specified using `PYTHON_VERSION` environment variable
