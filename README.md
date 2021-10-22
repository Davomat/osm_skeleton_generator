# Network Generator for OSM Indoor Data

This project is a continuation of Bettina Auschra's master's thesis. The core is to generate a network of osm ways based on the polyskel algorithm.


## Getting Started

To use the OSM parser you need to download at least the source folder and have python 3 installed (at least 3.7 is recommended).

The parser is designed to receive two to four additional arguments. Thus you must start it from the terminal or another command line tool. the first argument is the input file with its directory and name like `dir/to/file/filename.osm`. The second argument is the output file keeping the generated data. Note that the two files must differ. You may then add the optional arguments `-dd` and/or `-sw`. They will apply certain changes to the algorithm. For more information please read the master's thesis in the `doc` folder.

Here is an example command if you opened the whole project in an IDE, access python via the command `py`, and run the script out of your IDE terminal with both optional arguments:
```
py src/osm_parser.py data/nhg.osm data/nhg_ways.osm -dd -sw
```

## Testing Code Changes

In order to test whether changes or fixes in the code will also change the resulting file, two additional little scripts were made. The first script `is_same_file.py` will compare two xml files given as command line arguments. So after generating a new output file with changed code, always test if the result stays the same (if its supposed to be).
```
py src/is_same_file.py data/nhg_ways_original.osm data/nhg_ways_after-changes.osm
```

If the script tells you that there are differences, you can use the script `beautify_xml.py` to search for the resulted differences more easily. The generated osm files by the parser will always have just two lines. When using the mentioned script every element gets separated by a newline.
```
py src/beautify_xml.py data/nhg_ways_after-changes.osm
```

You will get a new file with a extended `-beautified.xml` suffix. By comparing two of these beautified files you will find differences quickly.
