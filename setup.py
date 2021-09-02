import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pythonconverter_pkg",

    version="0.0.1",
    author="Bastian Hamacher",
    author_email="b.hamacher@zera.de",
    description="Zera mobile device report generator",
    scripts=['ZeraConverter.py'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZeraGmbH/python-converter",
    zip_safe=False,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
