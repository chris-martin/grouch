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

def test_get_terms():
  scraper = create_scraper()
  html = read('bwckschd.p_disp_dyn_sched.html')
  terms = scraper.get_terms(html = html)
  assert terms == [
    ( Term(Term.FALL, 2012), '201208' ),
    ( Term(Term.SUMMER, 2012), '201205' ),
    ( Term(Term.SPRING, 2012), '201202' ),
    ( Term(Term.FALL, 2011), '201108' ),
  ]

def test_get_subjects():
  scraper = create_scraper()
  html = read('bwckgens.p_proc_term_date.html')
  subjects = scraper.get_subjects(html = html)
  assert subjects == [
    Subject('AE', 'Aerospace Engineering'),
    Subject('CSE', 'Computational Science & Engr'),
    Subject('CS', 'Computer Science'),
    Subject('NRE', 'Nuclear & Radiological Engr'),
    Subject('SOC', 'Sociology'),
    Subject('SPAN', 'Spanish'),
  ]
