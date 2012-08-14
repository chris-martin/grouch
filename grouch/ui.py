import argparse

from context import Context
from scraper import Scraper

def commandType(value):
  if value not in commands:
    raise argparse.ArgumentTypeError('must be one of: %s' \
      % ', '.join(command_list()))
  return commands[value]

commands = {}

def command():
  def g(f):
    commands[f.__name__] = f
    return f
  return g

def command_list():
  x = commands.keys()
  x.sort()
  return x

@command()
def terms(args):
  scraper = Scraper(Context())
  terms = scraper.get_terms()
  print('\n'.join(list([ str(t['term']) for t in terms ])))

def main():

  parser = argparse.ArgumentParser(
    description = 'Scraping for Oscar'
  )

  parser.add_argument(
    'command',
    type = commandType,
    help = 'One of the following options: %s' \
      % ', '.join(command_list()),
  )

  args = parser.parse_args()

  args.command(args)

if __name__ == '__main__':
  main()
