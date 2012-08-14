from BeautifulSoup import BeautifulSoup
from datetime import timedelta
from mechanize import Browser
from operator import itemgetter
import time

from term import Term

def oscar_url(procedure):
  return 'https://oscar.gatech.edu/pls/bprod/%s' % procedure

class Scraper:

  def __init__(self, context, enable_http = True):
    self.context = context
    self.enable_http = enable_http

  def browser_open(self, url, browser = None):

    if not self.enable_http:
      raise Exception('http is not enabled')

    if browser is None:
      browser = Browser()

    t = time.clock()
    response = browser.open(url)
    t = timedelta(seconds = time.clock() - t)

    self.context.logger.info('%s\n -> %s\n' % (t, url))
    return response

  #
  # Returns a list of terms, each given in the form
  # { 'id': '201208', 'term': Term(Term.FALL, 2012) },
  # sorted by chronology in reverse.
  #
  # The first item in this list is most likely the
  # term you are interested in.
  #
  # This method performs one http request, without
  # authentication.
  #
  def get_terms(self, html = None):

    if html is None:
      url = oscar_url('bwckschd.p_disp_dyn_sched')
      response = self.browser_open(url)
      html = response.read()

    soup = BeautifulSoup(html)
    select = soup.find('select', { 'id': 'term_input_id' })

    def iter_options():
      for o in select.findAll('option'):
        term = Term.parse(o.text)
        if term:
          attrs = dict(o.attrs)
          yield {
            'id': attrs['value'],
            'term': term,
          }

    options = list(iter_options())
    options.sort(key = itemgetter('term'), reverse = True)
    return options
