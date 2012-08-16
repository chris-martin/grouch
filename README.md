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

