from grouch import Term

def test_parse_spring():
  term = Term.parse('spring 2012')
  assert term
  assert term.get_season() == Term.SPRING
  assert term.get_year() == 2012

def test_parse_summer():
  term = Term.parse('Summer1998')
  assert term
  assert term.get_season() == Term.SUMMER
  assert term.get_year() == 1998

def test_parse_fall():
  term = Term.parse('FALL 2039')
  assert term
  assert term.get_season() == Term.FALL
  assert term.get_year() == 2039

def test_parse_failure_1():
  assert not Term.parse('')

def test_parse_failure_2():
  assert not Term.parse('Breakfast 2010')

def test_parse_failure_2():
  assert not Term.parse('Spring 2010 (View only)')

def test_cmp_1():
  assert Term(Term.FALL, 2009) < Term(Term.SPRING, 2010)

def test_cmp_2():
  assert Term(Term.FALL, 2009) > Term(Term.SUMMER, 2009)

def test_cmp_3():
  assert Term(Term.FALL, 2009) == Term(Term.FALL, 2009)
