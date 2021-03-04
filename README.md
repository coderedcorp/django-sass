django-sass
===========

The absolute simplest way to use [Sass](https://sass-lang.com/) with Django.
Pure Python, minimal dependencies, and no special configuration required.

[Source code on GitHub](https://github.com/coderedcorp/django-sass)


Status
------

|                        |                      |
|------------------------|----------------------|
| Python Package         | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-sass)](https://pypi.org/project/django-sass/) [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-sass)](https://pypi.org/project/django-sass/) [![PyPI - Wheel](https://img.shields.io/pypi/wheel/django-sass)](https://pypi.org/project/django-sass/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/django-sass)](https://pypi.org/project/django-sass/) [![PyPI](https://img.shields.io/pypi/v/django-sass)](https://pypi.org/project/django-sass/) |
| Build                  | [![Build Status](https://dev.azure.com/coderedcorp/cr-github/_apis/build/status/django-sass?branchName=main)](https://dev.azure.com/coderedcorp/cr-github/_build/latest?definitionId=10&branchName=main) [![Azure DevOps tests (branch)](https://img.shields.io/azure-devops/tests/coderedcorp/cr-github/10/main)](https://dev.azure.com/coderedcorp/cr-github/_build/latest?definitionId=10&branchName=main) [![Azure DevOps coverage (branch)](https://img.shields.io/azure-devops/coverage/coderedcorp/cr-github/10/main)](https://dev.azure.com/coderedcorp/cr-github/_build/latest?definitionId=10&branchName=main) |


Installation
------------

1. Install from pip.

```
pip install django-sass
```

2. Add to your `INSTALLED_APPS` (you only need to do this in a dev environment,
you would not want this in your production settings file, although it adds zero
overhead):

```python
INSTALLED_APPS = [
    ...,
    'django_sass',
]
```

3. Congratulations, you're done 😀


Usage
-----

In your app's static files, use Sass as normal. The only difference is that
you can **not** traverse upwards using `../` in `@import` statements. For example:

```
app1/
|- static/
   |- app1/
      |- scss/
         |- _colors.scss
         |- app1.scss
app2/
|- static/
   |- app2/
      |- scss/
         |- _colors.scss
         |- app2.scss
```

In `app2.scss` you could reference app1's and app2's `_colors.scss` import as so:

```scss
@import 'app1/scss/colors';
@import 'app2/scss/colors';
// Or since you are in app2, you can reference its colors with a relative path.
@import 'colors';
```

Then to compile `app2.scss` and put it in the `css` directory,
run the following management command (the `-g` will build a source map, which
is helpful for debugging CSS):

```
python manage.py sass app2/static/app2/scss/app2.scss app2/static/app2/css/app2.css -g
```

Or, you can compile the entire `scss` directory into
a corresponding `css` directory. This will traverse all subdirectories as well:

```
python manage.py sass app2/static/app2/scss/ app2/static/app2/css/
```

In your Django HTML template, reference the CSS file as normal:

```html
{% load static %}
<link href="{% static 'app2/css/app2.css' %}" rel="stylesheet">
```

✨✨ **Congratulations, you are now a Django + Sass developer!** ✨✨

Now you can commit those CSS files to version control, or run `collectstatic`
and deploy them as normal.

For an example project layout, see `testproject/` in this repository.


Watch Mode
----------

To have `django-sass` watch files and recompile them as they change (useful in
development), add the ``--watch`` flag.

```
python manage.py sass app2/static/app2/scss/ app2/static/app2/css/ --watch
```


Example: deploying compressed CSS to production
-----------------------------------------------

To compile minified CSS, use the `-t` flag to specify compression level (one of:
"expanded", "nested", "compact", "compressed"). The default is "expanded" which
is human-readable.

```
python manage.py sass app2/static/app2/scss/ app2/static/app2/css/ -t compressed
```

You may now optionally commit the CSS files to version control if so desired,
or omit them, whatever fits your needs better. Then run `collectsatic` as normal.

```
python manage.py collectstatic
```

And now proceed with deploying your files as normal.


Limitations
-----------

* `@import` statements must reference a path relative to a path in
  `STATICFILES_FINDERS` (which will usually be an app's `static/` directory or
  some other directory specified in `STATICFILES_DIRS`). Or they can reference a
  relative path equal to or below the current file. It does not support
  traversing up the filesystem (i.e. `../`).

  Legal imports:
  ```scss
  @import 'file-from-currdir';
  @import 'subdir/file';
  @import 'another-app/file';
  ```
  Illegal imports:
  ```scss
  @import '../file';
  ```

* Only files ending in `.scss` are supported for now.

* Only supports `-g`, `-p`, and `-t` options similar to `pysassc`. Ideally
  `django-sass` will be as similar as possible to the `pysassc` command line
  interface.

Feel free to file an issue or make a pull request to improve any of these
limitations. 🐱‍💻


Why django-sass?
----------------

Other packages such as
[django-libsass](https://github.com/torchbox/django-libsass) and
[django-sass-processor](https://github.com/jrief/django-sass-processor), while
nice packages, require `django-compressor` which itself depends on several other
packages that require compilation to install.

Installing `django-compressor` in your production web server requires a LOT of
extra bloat including a C compiler. It then will compile the Sass on-the-fly
while rendering the HTML templates. This is a wasteful use of CPU on your web
server.

Instead, `django-sass` lets you compile the Sass locally on your machine
*before* deploying, to reduce dependencies and CPU time on your production web
server. This helps keep things fast and simple.

* If you simply want to use Sass in development without installing a web of
  unwanted dependencies, then `django-sass` is for you.
* If you don't want to deploy any processors or compressors to your production
  server, then `django-sass` is for you.
* If you don't want to change the way you reference and serve static files,
  then `django-sass` is for you.
* And if you want the absolute simplest installation and setup possible for
  doing Sass, `django-sass` is for you too.

django-sass only depends on libsass (which provides pre-built wheels for
Windows, Mac, and Linux), and of course Django (any version).


Programmatically Compiling Sass
-------------------------------

You can also use `django-sass` in Python to programmatically compile the sass.
This is useful for build scripts and static site generators.

```python
from django_sass import compile_sass

# Compile scss and write to output file.
compile_sass(
    inpath="/path/to/file.scss",
    outpath="/path/to/output.css",
    output_style="compressed",
    precision=8,
    source_map=True
)
```

For more advanced usage, you can specify additional sass search paths outside
of your Django project by using the `include_paths` argument.

```python
from django_sass import compile_sass, find_static_paths

# Get Django's static paths.
dirs = find_static_paths()

# Add external paths.
dirs.append("/external/path/")

# Compile scss and write to output file.
compile_sass(
    inpath="/path/to/file.scss",
    outpath="/path/to/output.css",
    output_style="compressed",
    precision=8,
    source_map=True,
    include_paths=dirs,
)
```

Contributing
------------

To set up a development environment, first check out this repository, create a
venv, then:

```
(myvenv)$ pip install -r requirements-dev.txt
```

Before committing, run static analysis tools:

```
(myvenv)$ black .
(myvenv)$ flake8
(myvenv)$ mypy
```

Then run the unit tests:

```
(myvenv)$ pytest
```


Changelog
---------

#### 1.0.1
* Maintanence release, no functional changes.
* Add additional type hints within the codebase.
* Tested against Django 3.1
* Formatted code with `black`.

#### 1.0.0
* New: You can now use `django_sass` APIs directly in Python.
* Added unit tests.
* Code quality improvements.

#### 0.2.0
* New feature: `-g` option to build a source map (when input is a file, not a
  directory).

#### 0.1.2
* Fix: Write compiled CSS files as UTF-8.
* Change: Default `-p` precision from 5 to 8 for better support building
  Bootstrap CSS.

#### 0.1.1
* Fix: Create full file path if not exists when specifying a file output.

#### 0.1.0
* Initial release
