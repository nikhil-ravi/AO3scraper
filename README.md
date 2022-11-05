AO3scrapper
---
A python package to scrape works from a Fandom and the metadata, statistics, comments, kudos, and bookmarks of works.


Installation
---
Install the package using the following command:
```
pip install https://github.com/nikhil-ravi/AO3scrapper/archive/refs/heads/main.zip
```

Usage
---
The package may be used as follows:
```python
from AO3scrapper.Work import Work

w = Work(work_id=35477104)
```