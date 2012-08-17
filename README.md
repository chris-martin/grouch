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

