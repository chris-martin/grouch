from datetime import datetime, timedelta
import difflib
import os, os.path
import pickle
import string

from context import Context
from scraper import Scraper
from util import character_whitelist, makedirs

class Store:

  def __init__(self, context = None, enable_http = True,
      force_refresh = False):

    if context is None:
      context = Context()

    self.__context = context
    self.__enable_http = enable_http
    self.__private_scrapers = {}

    self.__public_scraper = Scraper(
      context = context,
      enable_http = enable_http,
    )

    self.__journal = Journal(
      context = context,
      force_refresh = force_refresh,
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

    def scrape():
      source = self.__public_scraper.get_terms()
      if source is not None:
        return Terms(source)

    journal = self.__journal.child('terms')

    return journal.get(Terms,
      shelf_life = timedelta(hours = 1),
      alternative = scrape)

  def __get_term_id(self, term = None):
    terms = self.__get_terms()
    if terms is None:
      return None
    if term is None:
      term = terms.list[0]
    return terms.dict[term]

  #
  # A list of Subjects, sorted by name.
  #
  def get_subjects(self, term = None):

    subjects = self.__get_subjects()

    if subjects is not None:
      return subjects.list

  def __get_subjects(self, term = None):

    term_id = self.__get_term_id(term)

    if term_id is None:
      return None

    def scrape():
      source = self.__public_scraper.get_subjects(term_id = term_id)
      if source is not None:
        return Subjects(source)

    journal = self.__journal.child('terms', term_id, 'subjects')

    return journal.get(Subjects,
      shelf_life = timedelta(hours = 1),
      alternative = scrape)

  def find_subject(self, s, term = None):

    subjects = self.__get_subjects(term)

    if subjects is not None:
      return subjects.find(s)

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

  def find(self, s):
    s = s.upper()

    for subject in self.list:
      if s == subject.get_id():
        return subject

    subject_names = list([ subject.get_name().upper()
      for subject in self.list ])
    matches = difflib.get_close_matches(s, subject_names, n = 1)

    if len(matches) != 0:
      subject_name = matches[0]
      for subject in self.list:
        if subject_name == subject.get_name().upper():
          return subject

def _safe_str(x):
  return character_whitelist(
    str(x),
    string.ascii_letters + string.digits + '_-'
  )

class Journal:

  def __init__(self, context, force_refresh, path = None):
    self.__context = context
    self.__force_refresh = force_refresh
    self.__path = path or []
    self.__children = {}
    self.__known = False
    self.__data = None

  def child(self, *path):
    if len(path) == 0:
      return self
    head = _safe_str(path[0])
    if len(head) == 0:
      raise Exception('bad path')
    if path[0] not in self.__children:
      self.__children[head] = Journal(
        context = self.__context,
        force_refresh = self.__force_refresh,
        path = self.__path + [ head ],
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

  def __filename(self):

    def is_file(f):
      full_filename = os.path.join(self.dir(), f)
      return os.path.isfile(full_filename)

    # List the files in this Journal's directory.
    files = filter(is_file, os.listdir(self.dir()))

    # The most recent file has the highest lexicographical name.
    if len(files) != 0:
      return max(files)

  def __know(self, data):
    self.__data = data
    self.__known = True

  def put(self, data):

    self.__know(data)
    now = datetime.utcnow()
    filename = os.path.join(self.dir(), now.strftime(_timestamp_format))

    self.__context.get_logger().info('Dump\n%s' % filename)

    fp = open(filename, 'w')
    try:
      data.dump(fp)
    finally:
      fp.close()

  def get(self, type_, shelf_life, alternative):

    # If data is cached in memory, always use that. Store objects
    # are intended to be used ephemerally, so we do not anticipate
    # any need to look up the same information more than once.
    if self.__known:
      return self.__data

    # Memoize the alternative function; we might call it twice.
    alternative = Memo(alternative)

    # If refresh is forced, immediately attempt to use the alternate.
    if self.__force_refresh:
      a = alternative()
      if a is not None:
        self.put(a)
        return a

    # Look in the directory to find a sufficiently recent file.
    filename = self.__filename()
    def fresh_file_exists():
      if filename is None:
        return False
      then = datetime.strptime(filename, _timestamp_format)
      age = datetime.utcnow() - then
      return age < shelf_life

    # If a recent file does not exist, attempt to use the alternate.
    if not fresh_file_exists():
      a = alternative()
      if a is not None:
        self.put(a)
        return a

    # If some file exists, use it.
    if filename is not None:
      full_filename = os.path.join(self.dir(), filename)
      self.__context.get_logger().info('Load\n%s' % full_filename)
      fp = open(full_filename, 'r')
      try:
        data = type_.load(fp)
      finally:
        fp.close()
      self.__know(data)
      return data

    # Alternate and file approaches have both failed.
    self.__know(None)

#
# Memoizes a value function.
#
class Memo:

  def __init__(self, fn):
    self.__fn = fn
    self.__value = None
    self.__executed = False

  def __call__(self):
    if self.__executed:
      return self.__value

    value = self.__fn()
    self.__fn = None
    self.__value = value
    self.__executed = True
    return value
