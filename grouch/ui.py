import argparse

from context import Context
from model import Term
from scraper import Scraper
from store import Store

def err(x):
  sys.stderr.write('%s\n' % x)

def command_type(value):
  if value not in commands:
    raise argparse.ArgumentTypeError('must be one of: %s' \
      % ', '.join(command_list()))
  return commands[value]

def term_type(value):
  term = Term.parse(value)
  if term is None:
    raise argparse.ArgumentTypeError('invalid format')
  return term

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
  terms = Store().get_terms()
  print('\n'.join(map(str, terms)))

@command()
def subjects(args):
  term = args.term
  if term is None:
    err('argument --term is required')
  else:
    subjects = Store().get_subjects(term)
    print('\n'.join(list([
      '\t'.join((s.get_id(), s.get_name())) for s in subjects
    ])))

def main():

  parser = argparse.ArgumentParser(
    description = 'Scraping for Oscar'
  )

  parser.add_argument(
    'command',
    type = command_type,
    help = 'One of the following options: %s' \
      % ', '.join(command_list()),
  )

  parser.add_argument(
    '--term',
    type = term_type,
    help = 'A semester and year such as "summer 2007"'
  )

  args = parser.parse_args()

  args.command(args)

if __name__ == '__main__':
  main()
