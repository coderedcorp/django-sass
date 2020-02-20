import os
from setuptools import setup, find_packages

from django_sass import __version__


with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf8") as readme:
    README = readme.read()

setup(
    name="django-sass",
    version=__version__,
    author="CodeRed LLC",
    author_email="info@coderedcorp.com",
    url="https://github.com/coderedcorp/django-sass",
    description=("The absolute simplest way to use Sass with Django. Pure Python, "
                 "minimal dependencies, and no special configuration required!"),
    long_description=README,
    long_description_content_type="text/markdown",
    license="BSD license",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "django",
        "libsass"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Environment :: Web Environment",
    ],
)
