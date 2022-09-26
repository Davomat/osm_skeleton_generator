# Network Generator for OSM Indoor Data

This project is a continuation of Bettina Auschra's master's thesis. The core is to generate a network of osm ways for navigation based on the polyskel algorithm.


## Getting Started

To use the OSM parser you need to download at least the source folder and have python 3 installed (at least 3.7 is recommended).

The parser is designed to receive at least two arguments. Thus you must run the script from the terminal or another command line tool. The first argument is the input file with its directory and name like `DIR/TO/FILE/filename.osm`. The second argument is the output file keeping the generated data. Note that the two files must differ.

You may then add up to 3 optional arguments:
- `-dd` will add ways constructed by the door-to-door approach (see the master's thesis in the `doc` folder)
- `-sw` will apply the simplify-way-algorithm to erase unneeded way points (see the master's thesis in the `doc` folder)
- `-2l` will skip the correcting to the output file making it xml conform (not recommended)

Here is an example command if you opened the whole project in an IDE, access python via the command `py`, run the script out of your IDE terminal, and use relative paths for the input and output:
```
py src/osm_parser.py data/nhg.osm data/nhg_ways.osm -dd -sw
```

## Dependencies

If you want a clean output file and therefore don't use the optional `-2l` argument, the parser imports BeautifulSoup and uses its xml parser. However, BeautifulSoup uses a html parser by default which is included in Python's standard library. To use the xml parser `lxml`, it needs to be installed as well. Depending on your system, you might install BeautifulSoup and lxml with commands like the following (Windows example):
```
pip install beautifulsoup4
pip install lxml
```


## Testing Code Changes

In order to test whether changes or fixes in the code will also change the resulting file, an additional script `is_same_file.py` can be used. It will compare two xml files given as command line arguments. So after generating a new output file with changed code, always test if the result stays the same (if its supposed to be).
```
py src/is_same_file.py data/nhg_ways_original.osm data/nhg_ways_after-changes.osm
```
