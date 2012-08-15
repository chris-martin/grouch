grouch
======

Scraping for Oscar

Usage Examples
--------------

```
$ python grouch/ui.py terms
Fall 2012
Summer 2012
Spring 2012
Fall 2011
```

```
$ python grouch/ui.py subjects | head -n 5
ACCT    Accounting
AE      Aerospace Engineering
AS      Air Force Aerospace Studies
APPH    Applied Physiology
ASE     Applied Systems Engineering
```

Caching
-------

Grouch keeps cached data in "~/.config/grouch/cache/".

Work in progress: Presently, this cache is never invalidated,
so you'll have to clear it manually to scrape new information.

If you run ui.py with the --offline flag, it will use the cache
exclusively, and not attempt to use the network for anything.

Logging
-------

HTTP and filesystem activity is logged to "~/.config/grouch/log".

