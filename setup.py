from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()


setup(
    name="epub-editor",
    packages=['epub_metadata'],
    package_dir={'epub_metadata': 'epub_metadata'},
    entry_points={
        'console_scripts': ['epub-editor=epub_editor:main'],
    },
    install_requires=[
        'lxml',
        'transliterate',
    ],
    version="0.0.3",
    url="https://github.com/shuvava/epub-metadata-editor",
    description="EPUB files metadata editor",
    license="GPL-3.0",
    keywords="epub editor",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",  # https://pypi.org/classifiers/
        "Environment :: Console",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
)
