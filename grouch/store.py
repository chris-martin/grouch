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

  def get_terms(self):
    data = self.data
    if not 'term list' in data:
      terms = self.public_scraper.get_terms()
      data['term list'] = list([ t['term'] for t in terms ])
      data['term dict'] = dict([ (t['term'], {'id': t['id']}) for t in terms ])
    return data['term list']

  def get_subjects(self, term):
    data = self.data
    self.get_terms()
    t = data['term dict'][term]
    if 'subject list' not in t:
      t['subject list'] = self.public_scraper.get_subjects(term_id = t['id'])
    return t['subject list']
