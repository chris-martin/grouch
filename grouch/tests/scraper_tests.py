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
    { 'id': '201208', 'term': Term(Term.FALL, 2012) },
    { 'id': '201205', 'term': Term(Term.SUMMER, 2012) },
    { 'id': '201202', 'term': Term(Term.SPRING, 2012) },
    { 'id': '201108', 'term': Term(Term.FALL, 2011) },
  ]
