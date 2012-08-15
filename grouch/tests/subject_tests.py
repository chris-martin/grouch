from grouch import Subject

def test():
  s = Subject(
    id = 'CS',
    name = 'Computer Science',
  )
  assert s.get_id() == 'CS'
  assert s.get_name() == 'Computer Science'
  assert str(s) == 'CS Computer Science'
  assert repr(s) == '<Subject id="CS" name="Computer Science">'
