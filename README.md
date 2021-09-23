# EPUB metadata editor
update epub files metadata

## Usage example 

``sh
./epub-upater.py --verbosity
    -f=~/test*.epub
    -a="some author"
    -b
``

## Arguments

|    Argument    | Description                 |
|:--------------:|:---------------------------:|
| `-f, --files`  | path to file(s)             |
| `-a, --author` | set author metadata         |
| `-t, --title`  | set title metadata          |
| `-b, --backup` | create backup before update |
