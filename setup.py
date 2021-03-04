import os
from setuptools import setup, find_packages


with open(
    os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf8"
) as readme:
    README = readme.read()

setup(
    name="django-sass",
    version="1.0.1",
    author="CodeRed LLC",
    author_email="info@coderedcorp.com",
    url="https://github.com/coderedcorp/django-sass",
    description=(
        "The absolute simplest way to use Sass with Django. Pure Python, "
        "minimal dependencies, and no special configuration required!"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    license="BSD license",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "django",
        "libsass",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
