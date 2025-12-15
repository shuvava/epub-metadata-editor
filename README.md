# EPUB metadata editor
update epub files metadata

## Usage example 

```sh
./epub-upater.py --verbosity
    -f=~/test*.epub
    -a="some author"
    -b
    --series="My Series"
    --num=1
    --rename
    --auto-series
```

## Arguments

|    Argument     | Description                                      |
|:--------------: |:------------------------------------------------:|
| `-f, --files`   | path to file(s)                                  |
| `-a, --author`  | set author metadata                              |
| `-t, --title`   | set title metadata                               |
| `-b, --backup`  | create backup before update                      |
| `-s, --series`  | set series metadata                              |
| `-n, --num`     | set series number metadata                       |
| `-r, --rename`  | rename file name to book-series_book-series-num  |
| `--auto-series` | auto-generate series metadata from file name     |
