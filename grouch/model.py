import re

_names = ['spring', 'summer', 'fall']

_pattern = re.compile('^([a-z]+)[ ]*([0-9]{4})$')

class Term:

  SPRING = 1
  SUMMER = 2
  FALL = 3

  @staticmethod
  def parse(s):
    m = re.match(_pattern, s.strip().lower())
    if m:
      season = m.group(1)
      if season in _names:
        season = 1 + _names.index(season)
        year = int(m.group(2))
        return Term(season, year)

  def get_season(self):
    return self.__season

  def get_year(self):
    return self.__year

  def __init__(self, season, year):
    assert season in range(1, len(_names) + 1)
    self.__season = season
    self.__year = year

  def __unicode__(self):
    return '%s %d' % (_names[self.__season - 1].title(), self.__year)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return '<Term season=%d year=%d>' % (self.__season, self.__year)

  def __cmp__(self, other):
    return (self.__year - other.__year) \
        or (self.__season - other.__season)

  def __hash__(self):
    return hash((self.__year, self.__season))

class Subject:

  def __init__(self, id, name):
    self.__id = id
    self.__name = name

  def get_id(self):
    return self.__id

  def get_name(self):
    return self.__name

  def __unicode__(self):
    return '%s %s' % (self.__id, self.__name)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return '<Subject id="%s" name="%s">' % (self.__id, self.__name)

  def __hash__(self):
    return hash((self.__id, self.__name))
