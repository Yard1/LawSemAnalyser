# LawSemAnalyser

## Requirements

* Python 3.7 or higher
* Docker 19.03.11 or higher, running from the same user account as Python

## Installation

Run `setup.py` to install the package.

## Quickstart

1. Create two folders - input and output
2. Grab HTML files using [ISAP API](http://isap.sejm.gov.pl/api/isap/#/default/downloadHTML) and save them in the input folder
3. Run:
```python
from LawSemAnalyser import SemAnalyser

analyser = SemAnalyser("path/to/output/folder", "path/to/input/folder")
analyser.analyse_docs()
```

The required Docker image will be pulled automatically.

## Author

Antoni Baum