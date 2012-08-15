import os, os.path

def makedirs(path):
  if not os.path.exists(path):
    os.makedirs(path)
