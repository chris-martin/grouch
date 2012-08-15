from context import Context
from scraper import Scraper

class Store:

  def __init__(self, context = None):

    if context is None:
      context = Context()

    self.context = context
    self.private_scrapers = {}
    self.public_scraper = Scraper(context = self.context)
    self.data = {}

  def add_private_scraper(username, password):
    self.private_scrapers[username] = Scraper(
      context = self.context,
      username = username,
      password = password,
    )

  #
  # A list of Terms, sorted by chronology in reverse.
  #
  def get_terms(self):
    data = self.data

    if not 'term list' in data:
      terms = self.public_scraper.get_terms()
      data['term list'] = list([ t[0] for t in terms ])
      data['term list'].sort(reverse = True)
      data['term dict'] = dict([ (t[0], { 'id': t[1] }) for t in terms ])

    return data['term list']

  #
  # A list of Subjects, sorted by name.
  #
  def get_subjects(self, term = None):
    data = self.data
    self.get_terms()

    if term is None:
      term = data['term list'][0]

    t = data['term dict'][term]

    if 'subject list' not in t:
      t['subject list'] = self.public_scraper.get_subjects(term_id = t['id'])
      t['subject list'].sort(key = lambda x: x.get_name())

    return t['subject list']
