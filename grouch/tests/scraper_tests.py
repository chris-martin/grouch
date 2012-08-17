from nose.tools import *

from grouch import Context, Scraper, Subject, Term

def file_path(name):
  return 'grouch/tests/%s' % name

def read(name):
  return open(file_path(name)).read()

def create_scraper():
  return Scraper(
    context = Context(),
    enable_http = False,
  )

# Terms

def terms_expected():
  return[
    ( Term(Term.FALL, 2012), u'201208' ),
    ( Term(Term.SUMMER, 2012), u'201205' ),
    ( Term(Term.SPRING, 2012), u'201202' ),
    ( Term(Term.FALL, 2011), u'201108' ),
  ]

def test_get_terms():
  scraper = create_scraper()
  html = read('bwckschd.p_disp_dyn_sched.html')
  terms = scraper.scrape_terms_html(html)
  assert_list_equal(terms, terms_expected())

# Subjects

def subjects_expected():
  return [
    Subject(u'AE', u'Aerospace Engineering'),
    Subject(u'CSE', u'Computational Science & Engr'),
    Subject(u'CS', u'Computer Science'),
    Subject(u'NRE', u'Nuclear & Radiological Engr'),
    Subject(u'SOC', u'Sociology'),
    Subject(u'SPAN', u'Spanish'),
  ]

def test_get_subjects():
  scraper = create_scraper()
  html = read('bwckgens.p_proc_term_date.html')
  subjects = scraper.scrape_subjects_html(html)
  assert_list_equal(subjects, subjects_expected())

# Courses

def courses_expected():
  def course(number, name, description = None):
    return {
      'number': number,
      'name': name,
      'description': description,
    }
  return [
    course(u'1050', u'Constructing Proofs',
      u'Techniques of rigorous argumentation, emphasizing '
      u'reading and writing of formal and informal proofs.  '
      u'Application of techniques to domains of relevance '
      u'to computer science.'),
    course(u'1171', u'Computing in MATLAB',
      u'For students with a solid introductory computing '
      u'background needing to demonstrate proficiency in '
      u'the MATLAB language.'),
    course(u'3510', u'Dsgn&Analysis-Algorithms',
      u'Basic techniques of design and analysis of '
      u'efficient algorithms for standard computational '
      u'problems. NP-Completeness.'),
    course(u'4911', u'Design Capstone Project'),
    course(u'8803', u'Special Topics',
      u'Special topics of current interest.  Treatment '
      u'of new developments in various areas of computing.'),
    course(u'8804', u'Special Topics',
      u'Special topics of current interest.  Treatment '
      u'of new developments in various areas of computing.'),
  ]

def test_get_courses_xml():
  scraper = create_scraper()
  xml = read('bwckctlg.p_display_courses.xml')
  courses = scraper.scrape_courses_xml(xml)
  assert_list_equal(courses, courses_expected())

def test_get_courses_html():
  scraper = create_scraper()
  html = read('bwckctlg.p_display_courses.html')
  courses = scraper.scrape_courses_html(html)
  assert_list_equal(courses, courses_expected())
