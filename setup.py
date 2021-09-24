from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="epub-editor",
    entry_points={
        'console_scripts': ['epub-editor=epub_editor:main'],
    },
    install_requires=[
        'lxml',
    ],
    version="0.0.1",
    url="https://github.com/shuvava/epub-metadata-editor",
    description="EPUB files metadata editor",
    license="GPL-3.0",
    keywords="epub editor",
    long_description=long_description,
    classifiers=[
        "License :: GPL-3.0 License",
    ],
)
