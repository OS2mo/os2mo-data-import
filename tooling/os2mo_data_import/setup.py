# -- coding: utf-8 --

from setuptools import setup

setup(
    name="os2mo-importer",
    version="0.0.1",
    description="Data import utility for os2mo",
    author="Magenta ApS",
    author_email="info@magenta.dk",
    license="MPL 2.0",
    packages=["os2mo_data_import"],
    zip_safe=False,
    install_requires=[
        "certifi==2018.10.15",
        "chardet==3.0.4",
        "idna==2.7",
        "requests==2.21.0",
        "urllib3==1.24.1"
    ]
)
