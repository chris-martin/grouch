from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from datetime import timedelta
from html2text import unescape
from operator import itemgetter
import re
import time
from urllib import urlencode
from urllib2 import Request, OpenerDirector, \
  HTTPDefaultErrorHandler, HTTPSHandler

from model import Subject, Term
from util import grouper

def oscar_url(procedure):
  return 'https://oscar.gatech.edu/pls/bprod/%s' % procedure

# Use this regex to identify a course number.
# Some lists contain pseudo-courses such as "3XXX".
# We have no use for those, and this will not match them.
course_number_re_fragment = '[0-9]{4}'

class Scraper:

  def __init__(self, context = None, enable_http = True):

    if context is None:
      context = Context()

    self.__context = context
    self.__enable_http = enable_http

  def fetch(self, request, opener = None):

    if not self.__enable_http:
      return (None, None)

    if opener is None:
      opener = OpenerDirector()
      opener.add_handler(HTTPDefaultErrorHandler())
      opener.add_handler(HTTPSHandler())

    t = time.clock()
    response = opener.open(request)
    body = response.read()
    t = timedelta(seconds = time.clock() - t)
    url = request.get_full_url()
    self.__context.get_logger().info('HTTP time: %s\n%s' % (t, url))
    return (response, body)

  def fetch_body(self, *args, **kwargs):
    (response, body) = self.fetch(*args, **kwargs)
    return body

  #
  # Terms
  # -------------------------------------------------------------
  #
  # A list of tuples in the form
  # ( Term(Term.FALL, 2012), '201208' ).
  #

  def get_terms(self):
    html = self.fetch_terms_html()
    if html is not None:
      return self.scrape_terms_html(html)

  def fetch_terms_html(self):
    url = oscar_url('bwckschd.p_disp_dyn_sched')
    return self.fetch_body(Request(url))

  def scrape_terms_html(self, html):

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
  # Subjects
  # -------------------------------------------------------------
  #
  # A list of Subject objects.
  #

  def get_subjects(self, term_id):
    html = self.fetch_subjects_html(term_id)
    if html is not None:
      return self.scrape_subjects_html(html)

  def fetch_subjects_html(self, term_id):
    return self.fetch_body(Request(
      url = oscar_url('bwckgens.p_proc_term_date'),
      data = urlencode([
        ('p_calling_proc', 'bwckschd.p_disp_dyn_sched'),
        ('p_term', str(term_id)),
      ]),
    ))

  def scrape_subjects_html(self, html):

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

  #
  # Courses
  # -------------------------------------------------------------
  #
  # A list of dicts with keys (number, name, description).
  #
  # This scrape has two methods: 'html', and 'xml' as a fallback.
  # Defaults to html first because I have observed that the XML
  # method, although easier to scrape, may contain less data.
  # For example, the course description for CS 4911 is missing
  # from the XML but present in the HTML.
  #
  def get_courses(self, term_id = None, subject_id = None, methods = None):

    if methods is None:
      methods = ['html', 'xml']

    def use_html():
      html = self.fetch_courses_html(term_id, subject_id)
      return self.scrape_courses_xml(html)

    def use_xml():
      xml = self.fetch_courses_xml(term_id, subject_id)
      return self.scrape_courses_xml(xml)

    method_dict = { 'html': use_html, 'xml': use_xml }

    for method in methods:
      courses = method_dict[method]()
      if len(courses) != 0:
        return courses

  def fetch_courses_html(self, term_id, subject_id):
    return self.fetch_body(Request(
      url = oscar_url('bwckctlg.p_display_courses'),
      data = urlencode([
        ('term_in', term_id),
        ('sel_subj', 'dummy'),
        ('sel_levl', 'dummy'),
        ('sel_schd', 'dummy'),
        ('sel_coll', 'dummy'),
        ('sel_divs', 'dummy'),
        ('sel_dept', 'dummy'),
        ('sel_attr', 'dummy'),
        ('sel_subj', subject_id),
        ('sel_crse_strt', ''),
        ('sel_crse_end', ''),
        ('sel_title', ''),
        ('sel_levl', '%'),
        ('sel_schd', '%'),
        ('sel_coll', '%'),
        ('sel_divs', '%'),
        ('sel_dept', '%'),
        ('sel_from_cred', ''),
        ('sel_to_cred', ''),
        ('sel_attr', '%'),
      ]),
    ))

  def scrape_courses_html(self, html):

    # Don't try to parse HTML with regular expressions, right?
    # Unfortunately, since Oscar doesn't believe in closing <tr>
    # tags, BeautifulSoup does not parse this table intelligibly.

    # This page consists of one giant single-column table.
    # Each course is represented by two consecutive rows.
    # The first row contains the course number and title.
    # The second row contains the description, plus some other things.

    def join(x): return map(lambda y: ''.join(y), x)
    rows = join(grouper(2, re.split('(<TR)', html)[1:]))

    title_re = re.compile('.*CLASS="nttitle".*>[A-Z]+ ('
      + course_number_re_fragment + ') - (.*)</A></TD>.*')

    def iter_courses():
      for (row1, row2) in grouper(2, rows):
        course = {}
        match = title_re.match(row1.replace('\n', ''))
        if match is None: continue
        course['number'] = match.group(1)
        course['name'] = match.group(2)
        soup = BeautifulSoup(row2)
        td = soup.find('td')
        d = td.contents[0].strip().replace('\n', ' ') or None
        course['description'] = d
        yield course

    return list(iter_courses())

  def fetch_courses_xml(self, term_id, subject_id):
    return self.fetch_body(Request(
      url = oscar_url('bwckctlg.xml'),
      data = urlencode([
        ('term_in', term_id),
        ('subj_in', '\t%s\t' % subject_id),
        ('title_in', '%%'),
        ('divs_in', '%'),
        ('dept_in', '%'),
        ('coll_in', '%'),
        ('schd_in', '%'),
        ('levl_in', '%'),
        ('attr_in', '%'),
        ('crse_strt_in', ''),
        ('crse_end_in', ''),
        ('cred_from_in', ''),
        ('cred_to_in', ''),
        ('last_updated', ''),
      ]),
    ))

  def scrape_courses_xml(self, xml):

    soup = BeautifulStoneSoup(xml)
    def text(node):
      if node is not None:
        return unescape(node.text)

    number_re = re.compile('^' + course_number_re_fragment + '$')

    def iter_courses():
      for inventory in soup.findAll('courseinventory'):
        def inventory_text(name):
          return text(inventory.find(name))
        number = inventory_text('coursenumber')
        if number_re.match(number):
          yield {
            'number': number,
            'name': inventory_text('courselongtitle'),
            'description': inventory_text('coursedescription'),
          }

    return list(iter_courses())

  #
  # Sections
  # -------------------------------------------------------------
  #
  # Work in progress.
  #

  def fetch_sections_html(self, term_id, subject_id):

    return self.fetch_body(Request(
      url = oscar_url('bwckschd.p_get_crse_unsec'),
      data = urlencode([
        ('term_in', term_id),
        ('sel_subj', 'dummy'),
        ('sel_day', 'dummy'),
        ('sel_schd', 'dummy'),
        ('sel_insm', 'dummy'),
        ('sel_camp', 'dummy'),
        ('sel_levl', 'dummy'),
        ('sel_sess', 'dummy'),
        ('sel_instr', 'dummy'),
        ('sel_ptrm', 'dummy'),
        ('sel_attr', 'dummy'),
        ('sel_subj', subject_id),
        ('sel_crse', ''),
        ('sel_title', ''),
        ('sel_schd', '%'),
        ('sel_from_cred', ''),
        ('sel_to_cred', ''),
        ('sel_camp', '%'),
        ('sel_ptrm', '%'),
        ('sel_instr', '%'),
        ('sel_attr', '%'),
        ('begin_hh', '0'),
        ('begin_mi', '0'),
        ('begin_ap', 'a'),
        ('end_hh', '0'),
        ('end_mi', '0'),
        ('end_ap', 'a'),
      ]),
    ))
