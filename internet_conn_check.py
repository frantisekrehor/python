import urllib2

try:
	urllib2.urlopen("http://www.seznam.cz", timeout=1)
	print "Working connection"
except urllib2.URLError:
	print "No internet connection"