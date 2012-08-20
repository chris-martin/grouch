from nose.tools import *

from grouch import *

def file_path(name):
  return 'grouch/tests/%s' % name

def read(name):
  return open(file_path(name)).read()

def create_scraper():
  return Scraper(enable_http = False)

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

# sections

def sections_expected():
  def section(course, name, crn):
    return {
      'course': course,
      'name': name,
      'crn': crn,
    }
  return [
    section(u'2110', u'A1', u'87133'),
    section(u'2110', u'A2', u'87134'),
    section(u'3451', u'A', u'84541'),
    section(u'3510', u'A', u'83096'),
    section(u'8803', u'3D', u'89839'),
    section(u'8803', u'ACN', u'90293'),
    section(u'9000', u'V05', u'86008'),
    section(u'9000', u'Z01', u'80283'),
  ]

def test_get_sections():
  scraper = create_scraper()
  html = read('bwckschd.p_get_crse_unsec.html')
  sections = scraper.scrape_sections_html(html)
  assert_list_equal(sections, sections_expected())

# section

def section_expected():
  return {
    'course': Course(u'CS', u'8803'),
    'section': u'ACN',
    'name': u'Special Topics',
    'capacity': Capacity(20, 9),
  }

def test_section():
  scraper = create_scraper()
  html = read('bwckschd.p_disp_detail_sched.html')
  section = scraper.scrape_section_html(html)
  assert_dict_equal(section, section_expected())
