from datetime import datetime, timedelta
import pickle
import os, os.path

from context import Context
from scraper import Scraper
from util import makedirs

class Store:

  def __init__(self, context = None):

    if context is None:
      context = Context()

    self.__context = context
    self.__private_scrapers = {}
    self.__public_scraper = Scraper(context = context)
    self.__journal = Journal(context = context)

  def add_private_scraper(username, password):
    self.__private_scrapers[username] = Scraper(
      context = self.context,
      username = username,
      password = password,
    )

  #
  # A list of Terms, sorted by chronology in reverse.
  #
  def get_terms(self):
    return self.__get_terms().list

  def __get_terms(self):

    journal = self.__journal.child('terms')
    (terms, age) = journal.get_latest(Terms)

    if terms is None:
      terms = Terms(self.__public_scraper.get_terms())
      journal.put(terms)

    return terms

  #
  # A list of Subjects, sorted by name.
  #
  def get_subjects(self, term = None):

    if term is None:
      term = self.__get_terms().list[0]

    term_id = self.__get_terms().dict[term]

    journal = self.__journal.child('terms', term_id, 'subjects')
    (subjects, age) = journal.get_latest(Subjects)

    if subjects is None:
      subjects = Subjects(self.__public_scraper.get_subjects(term_id = term_id))
      journal.put(subjects)

    return subjects.list

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

  def get_latest(self, type_):

    if self.__data is not None:
      return (self.__data, timedelta())

    files = os.listdir(self.dir())
    files = filter(lambda f: os.path.isfile(os.path.join(self.dir(), f)), files)

    if len(files) == 0:
      return (None, None)

    filename = max(files)
    full_filename = os.path.join(self.dir(), filename)

    fp = open(full_filename, 'r')
    try:
      data = type_.load(fp)
    finally:
      fp.close()

    self.__data = data
    age = datetime.utcnow() - datetime.strptime(filename, _timestamp_format)
    return (data, age)
