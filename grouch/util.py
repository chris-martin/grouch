import os, os.path
import string

def makedirs(path):
  if not os.path.exists(path):
    os.makedirs(path)

def character_whitelist(x, whitelist):
  return x.translate(None, string.maketrans(
    whitelist, ' ' * len(whitelist)
  ))
