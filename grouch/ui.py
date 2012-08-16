import argparse
import logging
import sys

from context import Context
from model import Term
from scraper import Scraper
from store import Store

def err(x):
  sys.stderr.write('%s\n' % x)

def not_available():
  err('Information not available.')

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

def log_handler():
  handler = logging.StreamHandler(sys.stdout)
  formatter = logging.Formatter(
    '%(asctime)s %(levelname)s - %(message)s\n')
  handler.setFormatter(formatter)
  return handler

def store(args):
  context = Context()
  if args.verbose:
    print ''
    context.get_logger().addHandler(log_handler())
  return Store(
    context = context,
    enable_http = args.enable_http,
    force_refresh = args.refresh,
  )

@command()
def terms(args):
  terms = store(args).get_terms()
  if terms is None:
    not_available()
  else:
    print('\n'.join(map(str, terms)))

@command()
def subjects(args):
  subjects = store(args).get_subjects(term = args.term)
  if subjects is None:
    not_available()
  else:
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
    help = 'A semester and year such as "summer 2007"' \
      ' (defaults to the latest term)',
  )

  parser.add_argument(
    '--offline',
    dest = 'enable_http',
    action = 'store_false',
    help = 'Disable network access and use only cached data',
  )

  parser.add_argument(
    '--refresh',
    action = 'store_true',
    help = 'Fetch the most recent information from the ' \
      'server, regardless of the cache state'
  )

  parser.add_argument(
    '--verbose',
    action = 'store_true',
    help = 'Print logging output',
  )

  args = parser.parse_args()

  args.command(args)

if __name__ == '__main__':
  main()
