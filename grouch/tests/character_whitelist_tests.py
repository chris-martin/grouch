from grouch.util import character_whitelist

def test_xyyzy():
  x = 'regrsXnl je45n34gYt35go48uyZghZ345hg 4t3Y45yt4  '
  assert character_whitelist(x, 'XYZ') == 'XYZZY'

def test_empty():
  assert character_whitelist('', 'XYZ') == ''

def test_nomatch():
  x = 'rgerg erthgtrerw goirehgfj8934 tg453rg 34tg'
  assert character_whitelist(x, 'XYZ') == ''
