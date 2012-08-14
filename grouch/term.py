import re

_names = ['spring', 'summer', 'fall']

_pattern = re.compile('^([a-z]+) ([0-9]{4})$')

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

  def __init__(self, season, year):
    assert season in range(1, len(_names) + 1)
    self.season = season
    self.year = year

  def __unicode__(self):
    return '%s %d' % (_names[self.season - 1].title(), self.year)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __repr__(self):
    return '<Term season=%d year=%d>' % (self.season, self.year)

  def __cmp__(self, other):
    return (self.year - other.year) \
        or (self.season - other.season)
