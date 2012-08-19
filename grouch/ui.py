import argparse
import logging
import sys
from textwrap import TextWrapper

from context import Context
from model import Course, Term
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

@command()
def terms(args, store):
  terms = store.get_terms()
  if terms is None:
    not_available()
  else:
    for term in terms:
      print(str(term))

@command()
def subjects(args, store):
  subjects = store.get_subjects(term = args.term)
  if subjects is None:
    not_available()
  else:
    for s in subjects:
      print('\t'.join((s.get_id(), s.get_name())))

@command()
def courses(args, store):
  if args.subject is None:
    err('--subject is required')
  else:
    courses = store.get_courses(
      term = args.term,
      subject = args.subject,
    )
    if courses is None:
      not_available()
    else:
      pad = 2
      wrapper = TextWrapper(
        initial_indent = ' ' * (4 + pad),
        subsequent_indent = ' ' * (4 + pad),
      )
      for course in courses:
        print((' ' * pad).join((
          course['number'],
          course['name'],
        )))
        print('')
        d = course['description']
        if d is not None:
          for line in wrapper.wrap(d):
            print line
          print('')

@command()
def sections(args, store):
  if args.subject is None:
    err('--subject is required')
  else:
    courses = store.get_courses(
      term = args.term,
      subject = args.subject,
    )
    pad = 2
    wrapper = TextWrapper(
      initial_indent = ' ' * pad,
      subsequent_indent = ' ' * (4 + pad),
    )
    for course in courses:
      course = Course(args.subject, course['number'])
      sections = store.get_sections(
        course = course,
        term = args.term,
      )
      if len(sections) != 0:
        print(course.get_number() + '\n'.join(
          wrapper.wrap(' '.join([
            section['name'] for section in sections
          ]))
        ))
        print ''


def main():

  parser = argparse.ArgumentParser(
    description = 'Scraping for Oscar'
  )

  parser.add_argument(
    'command',
    type = command_type,
    help = 'One of the following options: %s' \
      % ', '.join(command_list()),
    nargs = '?',
  )

  parser.add_argument(
    '--term',
    type = term_type,
    help = 'A semester and year such as "summer 2007"' \
      ' (defaults to the latest term)',
    metavar = '',
  )

  parser.add_argument(
    '--subject',
    help = 'A subject such as "cs" or "comp sci"',
    metavar = '',
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

  parser.add_argument(
    '--quiet',
    dest = 'chatty',
    action = 'store_false',
    help = 'Do not print anything beyond the output '
      'requested by the command'
  )

  args = parser.parse_args()

  context = Context()

  if args.chatty:
    print ''

  if args.verbose:
    context.get_logger().addHandler(log_handler())

  store = Store(
    context = context,
    enable_http = args.enable_http,
    force_refresh = args.refresh,
  )

  if args.subject is not None:
    subject = store.find_subject(args.subject)
    if args.chatty:
      print('Subject: %s\n' % unicode(subject))
    args.subject = subject

  if args.command:
    args.command(args, store)

  if args.chatty:
    print ''

if __name__ == '__main__':
  main()
