links
=====

[links][] collected by [narf][]

  [links]:  https://links.narf.pl/
  [narf]:   https://narf.pl/


## Running locally

```
brew install pyenv-virtualenv
pyenv virtualenv links
pyenv activate links
pip install -r requirements-local.txt

./manage.py runserver
```


## Running on [Render](https://render.com)

this is a static site

#### build command

    pip install -r requirements.txt && PYTHONPATH=.:$PYTHONPATH python app/generator.py

#### publish directory

    app/build

#### Python version

specified using `PYTHON_VERSION` environment variable

#### redirects

- `/feed` -> `/feed.xml`
