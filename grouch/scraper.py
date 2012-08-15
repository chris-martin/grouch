from BeautifulSoup import BeautifulSoup
from datetime import timedelta
from operator import itemgetter
import time
from urllib import urlencode
from urllib2 import Request, OpenerDirector, \
  HTTPDefaultErrorHandler, HTTPSHandler

from model import Subject, Term

def oscar_url(procedure):
  return 'https://oscar.gatech.edu/pls/bprod/%s' % procedure

class Scraper:

  def __init__(self, context, enable_http = True):
    self.context = context
    self.enable_http = enable_http

  def fetch(self, request, opener = None):

    if not self.enable_http:
      raise Exception('http is not enabled')

    if opener is None:
      opener = OpenerDirector()
      opener.add_handler(HTTPDefaultErrorHandler())
      opener.add_handler(HTTPSHandler())

    t = time.clock()
    response = opener.open(request)
    t = timedelta(seconds = time.clock() - t)
    url = request.get_full_url()
    self.context.logger.info('%s\n -> %s\n' % (t, url))
    return response

  #
  # A list of tuples in the form
  # ( Term(Term.FALL, 2012), '201208' ).
  #
  # Performs one http request, without authentication.
  #
  def get_terms(self, html = None):

    if html is None:
      url = oscar_url('bwckschd.p_disp_dyn_sched')
      response = self.fetch(Request(url))
      html = response.read()

    soup = BeautifulSoup(html)
    select = soup.find('select', { 'id': 'term_input_id' })

    def iter_options():
      for o in select.findAll('option'):
        term = Term.parse(o.text)
        if term:
          attrs = dict(o.attrs)
          yield (term, attrs['value'])

    return list(iter_options())

  #
  # A list of Subjects.
  #
  # Performs one http request, without authentication.
  #
  def get_subjects(self, html = None, term_id = None):

    if html is None:

      if term_id is None:
        raise Exception('either html or term_id is required')

      response = self.fetch(Request(
        url = oscar_url('bwckgens.p_proc_term_date'),
        data = urlencode({
          'p_calling_proc': 'bwckschd.p_disp_dyn_sched',
          'p_term': str(term_id),
        }),
      ))
      html = response.read()

    soup = BeautifulSoup(html)
    select = soup.find('select', { 'id': 'subj_id' })

    def iter_options():
      for o in select.findAll('option'):
        attrs = dict(o.attrs)
        yield Subject(
          id = attrs['value'],
          name = o.text,
        )

    return list(iter_options())
