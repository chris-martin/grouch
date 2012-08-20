from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from datetime import datetime, timedelta
from html2text import unescape
from operator import itemgetter
import os.path
import re
import string
import time
from urllib import urlencode
from urllib2 import Request, OpenerDirector, \
  HTTPDefaultErrorHandler, HTTPSHandler

from context import Context
from model import Capacity, Course, Subject, Term
from util import character_whitelist, grouper, makedirs

def oscar_url(procedure):
  return 'https://oscar.gatech.edu/pls/bprod/%s' % procedure

# Regex for a course number.
# Some lists contain pseudo-courses such as "3XXX".
# We have no use for those, and this will not match them.
course_number_re_fragment = '[0-9]{4}'

# Regex for a section name.
# Some examples of section names: "A", "B2", "MAS", "3D".
section_name_re_fragment = '[A-Za-z0-9]+'

def _safe_str(x):
  return character_whitelist(
    str(x),
    string.ascii_letters + string.digits + '_-'
  )

class Scraper:

  def __init__(self, context = None, enable_http = True,
      log_http = False):

    if context is None:
      context = Context()

    self.__context = context
    self.__enable_http = enable_http
    self.__log_http = log_http

  def fetch(self, request, opener = None, summary = None):

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

    if self.__log_http:
      log_dir = os.path.join(self.__context.get_config_dir(), 'http-log')
      makedirs(log_dir)
      log_file = os.path.join(log_dir,
        datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f'))
      if summary is not None:
        log_file += '-' + _safe_str(summary)
      fp = open(log_file, 'w')
      fp.write('\n\n'.join([
        request.get_full_url(),
        request.get_data() or 'No request data',
        body or 'No response body',
      ]))
      fp.close()

    return (response, body)

  def fetch_body(self, *args, **kwargs):
    (response, body) = self.fetch(*args, **kwargs)
    return body

  #
  # Terms
  # -------------------------------------------------------------
  #
  # A list of tuples in the form
  # ( Term(Term.FALL, 2012), u'201208' )
  #

  def get_terms(self):
    html = self.fetch_terms_html()
    if html is not None:
      return self.scrape_terms_html(html)

  def fetch_terms_html(self):
    url = oscar_url('bwckschd.p_disp_dyn_sched')
    return self.fetch_body(
      request = Request(url),
      summary = 'fetch-terms-html',
    )

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
    return self.fetch_body(
      request = Request(
        url = oscar_url('bwckgens.p_proc_term_date'),
        data = urlencode([
          ('p_calling_proc', 'bwckschd.p_disp_dyn_sched'),
          ('p_term', str(term_id)),
        ]),
      ),
      summary = 'fetch-subjects-html',
    )

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
  # A list of dicts in the form {
  #   'number': u'1050',
  #   'name': u'Constructing Proofs',
  #   'description': u'Techniques of rigorous argumentation.'
  # }
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
      return self.scrape_courses_html(html)

    def use_xml():
      xml = self.fetch_courses_xml(term_id, subject_id)
      return self.scrape_courses_xml(xml)

    method_dict = { 'html': use_html, 'xml': use_xml }

    for method in methods:
      courses = method_dict[method]()
      if len(courses) != 0:
        return courses
      else:
        self.__context.get_logger().error(
          'get_courses (%s) failed' % method)

  def fetch_courses_html(self, term_id, subject_id):
    return self.fetch_body(
      request = Request(
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
      ),
      summary = 'fetch-courses-html',
    )

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

    title_re = re.compile('CLASS="nttitle".*>[A-Z]+ ('
      + course_number_re_fragment + ') - (.*)</A></TD>')

    def iter_courses():
      for (row1, row2) in grouper(2, rows):
        course = {}
        match = title_re.search(row1.replace('\n', ''))
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
    return self.fetch_body(
      request = Request(
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
      ),
      summary = 'fetch-courses-xml',
    )

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
  # A list of dicts in the form {
  #   'crn': '87134',
  #   'course': '2110',
  #   'name': 'A2',
  # }
  #

  def get_sections(self, term_id, subject_id):
    html = self.fetch_sections_html(term_id, subject_id)
    if html is not None:
      return self.scrape_sections_html(html)

  def fetch_sections_html(self, term_id, subject_id):
    return self.fetch_body(
      request = Request(
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
      ),
      summary = 'fetch-sections-html',
    )

  def scrape_sections_html(self, html):

    def join(x): return map(lambda y: ''.join(y), x)
    rows = join(grouper(2, re.split(
      '(<TR>\n<TH CLASS="ddtitle")', html)[1:]))

    title_re = re.compile('<TH CLASS="ddtitle".*><A .*>'
      '.* - ([0-9]+) - .* (' + course_number_re_fragment + ')'
      ' - (' + section_name_re_fragment + ')</A></TH>')

    def iter_sections():
      for row in rows:
        section = {}
        match = title_re.search(row.replace('\n', ''))
        if match is None: continue
        yield {
          'crn': match.group(1),
          'course': match.group(2),
          'name': match.group(3),
        }

    return list(iter_sections())

  #
  # Section
  # -------------------------------------------------------------
  #
  # A dict in the form {
  #   'course': Course('CS', '8803'),
  #   'section': 'ACN',
  #   'name': 'Algorithms for Complex Netwks',
  #   'capacity': Capacity(20, 9),
  # }
  #

  def get_section(self, term_id, crn):
    html = self.fetch_section_html(term_id, crn)
    if html is not None:
      return self.scrape_section_html(html)

  def fetch_section_html(self, term_id, crn):
    return self.fetch_body(
      request = Request('%s?%s' % (
        oscar_url('bwckschd.p_disp_detail_sched'),
        urlencode([
          ('term_in', term_id),
          ('crn_in', crn),
        ]),
      )),
      summary = 'fetch-section-html',
    )

  def scrape_section_html(self, html):

    section = {}

    soup = BeautifulSoup(html)

    header = soup.find('th', 'ddlabel')
    if header is None:
      return None
    match = re.match('(.*) - [0-9]+ - (.*) (' + course_number_re_fragment + ')'
      ' - (' + section_name_re_fragment + ')$', header.text.strip())
    if match is None:
      return None
    section['name'] = match.group(1)
    section['course'] = Course(
      subject = match.group(2),
      number = match.group(3),
    )
    section['section'] = match.group(4)

    tables = soup.findAll('table', 'datadisplaytable')
    if len(tables) >= 2:
      table = tables[1]
      trs = table.findAll('tr')
      if len(trs) >= 2:
        tr = trs[1]
        tds = tr.findAll('td')
        if len(tds) > 2:
          try:
            section['capacity'] = Capacity(
              max = int(tds[0].text),
              current = int(tds[1].text),
            )
          except ValueError: pass

    return section
