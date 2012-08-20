grouch
======

Scraping for Oscar

Usage Examples
--------------

```
$ grouch terms

Fall 2012
Summer 2012
Spring 2012
Fall 2011
```

```
$ grouch subjects | head -n 5

ACCT    Accounting
AE      Aerospace Engineering
AS      Air Force Aerospace Studies
APPH    Applied Physiology
ASE     Applied Systems Engineering
```

```
$ grouch courses --subject computars | head -n 15

Subject: CS Computer Science

1050  Constructing Proofs

      Techniques of rigorous argumentation, emphasizing reading and
      writing of formal and informal proofs.  Application of
      techniques to domains of relevance to computer science.

1100  Freshman Leap Seminar

      Small group discussions with first year students are led by one
      or more faculty members and include a variety of foundational,
      motivational, and topical subjects for computationalist.
```

```
$ grouch sections --subject physics | head -n 13

Subject: PHYS Physics

2021  A

2211  A A01 A02 A03 A04 A05 A06 A07 A08 A09 B B01 B02 B03 B04 B05 B06 B07
      B08 B09 M M01 M02 M03 M04 M05 M06 M07 M08 N N01 N02 N03 N04 N05
      N06 N07 N08

2212  G G01 G02 H H01 H02 H03 H04 H05 H06 H07 H08 H09 HP J J01 J02 J03 J04
      J05 J06 J07 J08 J09 N N01 N02 N03 N04 N05 N07 N08 P P01 P02 P03
      P04 P05 P06 P07 P08 Q Q01 Q02 Q03 Q04 Q05 Q07 Q08
```

```
$ grouch crn --course cs2110 --section A2

87134

$ crn --subject cs --number 2110 --section A2

87134
```

Installation
------------

```
python setup.py install
```

This installs the ```grouch``` Python module and the
```grouch``` script demonstrated in the examples.

Caching
-------

Grouch keeps cached data in ```~/.config/grouch/cache/```.

The cache is time-invalidated and is designed to provide
reasonably current information while avoiding excessive
server utilization.

You can set the ```--refresh``` flag to ignore the cache timer
and force server reloads.
The ```--offline``` flag has the opposite effect, utilizing the
cache exclusively without touching the network at all.

Logging
-------

HTTP and filesystem activity is logged to ```~/.config/grouch/log```.
Use the ```--verbose``` flag to also log to the console.

For debugging, you can use the ```--log-http``` flag to log all
HTTP requests and responses to ```~/.config/grouch/log-http/```.

