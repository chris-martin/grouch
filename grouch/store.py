from datetime import datetime, timedelta
import pickle
import os, os.path

from context import Context
from scraper import Scraper
from util import makedirs

class Store:

  def __init__(self, context = None, enable_http = True,
      force_refresh = False):

    if context is None:
      context = Context()

    self.__context = context
    self.__enable_http = enable_http
    self.__force_refresh = force_refresh
    self.__private_scrapers = {}

    self.__public_scraper = Scraper(
      context = context,
      enable_http = enable_http,
    )

    self.__journal = Journal(
      context = context
    )

  def add_private_scraper(username, password):
    self.__private_scrapers[username] = Scraper(
      context = self.__context,
      enable_http = self.__enable_http,
      username = username,
      password = password,
    )

  #
  # A list of Terms, sorted by chronology in reverse.
  #
  def get_terms(self):

    terms = self.__get_terms()

    if terms is not None:
      return terms.list

  def __get_terms(self):

    journal = self.__journal.child('terms')

    terms = None

    if not self.__force_refresh:
      (terms, fresh) = journal.get_latest(Terms, timedelta(hours = 1))

    if self.__force_refresh or not fresh:
      source = self.__public_scraper.get_terms()
      if source is not None:
        terms = Terms(source)
        journal.put(terms)

    return terms

  #
  # A list of Subjects, sorted by name.
  #
  def get_subjects(self, term = None):

    subjects = self.__get_subjects()

    if subjects is not None:
      return subjects.list

  def __get_subjects(self, term = None):

    terms = self.__get_terms()

    if terms is None:
      return None

    if term is None:
      term = terms.list[0]

    term_id = terms.dict[term]

    journal = self.__journal.child('terms', term_id, 'subjects')

    subjects = None

    if not self.__force_refresh:
      (subjects, fresh) = journal.get_latest(Subjects, timedelta(hours = 1))

    if self.__force_refresh or not fresh:
      source = self.__public_scraper.get_subjects(term_id = term_id)
      if source is not None:
        subjects = Subjects(source)
        journal.put(subjects)

    return subjects

_timestamp_format = '%Y-%m-%d-%H-%M-%S-%f'

class Terms:

  def __init__(self, source):
    self.source = source
    self.list = list([ t[0] for t in source ])
    self.list.sort(reverse = True)
    self.dict = dict(source)

  def dump(self, fp):
    pickle.dump(self.source, fp)

  @staticmethod
  def load(fp):
    return Terms(pickle.load(fp))

class Subjects:

  def __init__(self, source):
    self.source = source
    self.list = list(source)
    self.list.sort(key = lambda x: x.get_name())

  def dump(self, fp):
    pickle.dump(self.source, fp)

  @staticmethod
  def load(fp):
    return Subjects(pickle.load(fp))

class Journal:

  def __init__(self, context, path = None):
    self.__context = context
    self.__path = path or []
    self.__children = {}
    self.__data = None

  def child(self, *path):
    if len(path) == 0:
      return self
    if path[0] not in self.__children:
      self.__children[path[0]] = Journal(
        context = self.__context,
        path = self.__path + [ path[0] ],
      )
    return self.__children[path[0]].child(*path[1:])

  def dir(self):
    d = os.path.join(
      self.__context.get_config_dir(),
      'cache',
      os.path.join(*self.__path)
    )
    makedirs(d)
    return d

  def put(self, data):

    self.__data = data
    now = datetime.utcnow()
    filename = os.path.join(self.dir(), now.strftime(_timestamp_format))

    self.__context.get_logger().info('Dump\n%s' % filename)

    fp = open(filename, 'w')
    try:
      data.dump(fp)
    finally:
      fp.close()

  def get_latest(self, type_, shelf_life):

    if self.__data is not None:
      return (self.__data, True)

    files = os.listdir(self.dir())
    files = filter(lambda f: os.path.isfile(os.path.join(self.dir(), f)), files)

    if len(files) == 0:
      return (None, False)

    filename = max(files)
    full_filename = os.path.join(self.dir(), filename)

    self.__context.get_logger().info('Load\n%s' % full_filename)

    fp = open(full_filename, 'r')
    try:
      data = type_.load(fp)
    finally:
      fp.close()

    self.__data = data
    age = datetime.utcnow() - datetime.strptime(filename, _timestamp_format)
    return (data, age < shelf_life)
