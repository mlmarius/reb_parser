```python
from reb_parser.parser import RebFile
rf = RebFile('testdata/2015198_10_16_38')
print rf.toDict()     # print reb as a data structure
print rf.raw          # print raw reb
```
