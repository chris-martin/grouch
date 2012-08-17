from itertools import izip_longest
import os, os.path
import string

def makedirs(path):
  if not os.path.exists(path):
    os.makedirs(path)

def character_whitelist(x, whitelist):
  return x.translate(None, string.maketrans(
    whitelist, ' ' * len(whitelist)
  ))

#
# Collect data into fixed-length chunks or blocks
# grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
#
def grouper(n, iterable, fillvalue = None):
  args = [ iter(iterable) ] * n
  return izip_longest(fillvalue = fillvalue, *args)
