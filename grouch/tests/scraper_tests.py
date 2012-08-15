from grouch import Context, Scraper, Term
from pprint import pprint

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
