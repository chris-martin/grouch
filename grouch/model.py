import re

_season_names = [u'spring', u'summer', u'fall']

_term_pattern = re.compile('^([a-z]+)[ ]*([0-9]{4})$')

class Term:

  SPRING = 1
  SUMMER = 2
  FALL = 3

  @staticmethod
  def parse(s):
    m = re.match(_term_pattern, s.strip().lower())
    if m:
      season = m.group(1)
      if season in _season_names:
        season = 1 + _season_names.index(season)
        year = int(m.group(2))
        return Term(season, year)

  def get_season(self):
    return self.__season

  def get_year(self):
    return self.__year

  def __init__(self, season, year):
    assert season in range(1, len(_season_names) + 1)
    self.__season = season
    self.__year = year

  def __unicode__(self):
    return u'%s %d' % (
      _season_names[self.__season - 1].title(),
      self.__year
    )

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return u'<Term season=%d year=%d>' % \
      (self.__season, self.__year)

  def __key(self):
    return (self.__year, self.__season)

  def __cmp__(self, other):
    return cmp(self.__key(), other.__key())

  def __hash__(self):
    return hash(self.__key())

class Subject:

  def __init__(self, id, name):
    self.__id = id
    self.__name = name

  def get_id(self):
    return self.__id

  def get_name(self):
    return self.__name

  def __unicode__(self):
    return u'%s %s' % (self.__id, self.__name)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return u'<Subject id="%s" name="%s">' % \
      (self.__id, self.__name)

  def __key(self):
    return (self.__id, self.__name)

  def __cmp__(self, other):
    return cmp(self.__key(), other.__key())

  def __hash__(self):
    return hash(self.__key())

_course_pattern = re.compile('^([A-Z ]+)([0-9]{4})$')

class Course:

  @staticmethod
  def parse(s):
    m = re.match(_course_pattern, s.strip().upper())
    if m:
      subject = m.group(1)
      number = m.group(2)
      return Course(subject, number)

  def __init__(self, subject, number):
    self.__subject = subject
    self.__number = number

  def get_subject(self):
    return self.__subject

  def get_number(self):
    return self.__number

  def __unicode__(self):
    return u'%s %s' % (
      self.__subject,
      self.__number
    )

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return u'<Course subject="%s" number="%s">' % \
      (self.__subject, self.__number)

  def __key(self):
    return (self.__subject, self.__number)

  def __cmp__(self, other):
    return cmp(self.__key(), other.__key())

  def __hash__(self):
    return hash(self.__key())

class Capacity:

  def __init__(self, max, current):
    self.__max = max
    self.__current = current

  def get_max():
    return self.__max

  def get_current():
    return self.__current

  def __unicode__(self):
    return u'%d of %d slots filled' % (
      self.__current,
      self.__max
    )

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return u'<Capacity max="%d" current="%d">' % \
      (self.__max, self.__current)

  def __key(self):
    return (self.__max, self.__current)

  def __cmp__(self, other):
    return cmp(self.__key(), other.__key())

