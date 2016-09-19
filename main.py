# -*- coding: utf-8 -*-
import datetime
import re

from lxml.etree import parse


ISO4217_XML_URL = 'http://www.currency-iso.org/dam/downloads/lists/list_one.xml'  # noqa: E501
DATE_RE = re.compile(r'^\s*(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)\s*$')
FEED_PATH = '/feed.xml'


def get_updated():
    tree = parse(ISO4217_XML_URL)
    match = DATE_RE.match(tree.getroot().attrib['Pblshd'])
    kwargs = {k: int(v) for k, v in match.groupdict().iteritems()}
    return datetime.date(**kwargs)


def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    scheme = environ.get('wsgi.url_scheme', 'http').strip().lower()
    host = environ.get('HTTP_HOST',
                       environ.get('SERVER_NAME', '')).strip().lower()
    urljoin = '{}://{}{}'.format
    if path != FEED_PATH:
        new_url = urljoin(scheme, host, FEED_PATH)
        start_response('301 Moved Permanently', [
            ('Content-Type', 'text/plain'),
            ('Location', new_url),
        ])
        return '',
    url = urljoin(scheme, host, path)
    updated = get_updated()
    start_response('200 OK', [('Content-Type', 'application/atom+xml')])
    return '''\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>{url}</id>
  <title>ISO 4217 &#x2014; Currency codes</title>
  <link rel="self" href="{url}" type="application/atom+xml" />
  <link href="http://www.iso.org/iso/home/standards/currency_codes.htm"
        type="text/html" />
  <link href="http://www.currency-iso.org/dam/downloads/lists/list_one.xml"
        type="text/xml" />
  <updated>{updated:%Y-%m-%d}T00:00:00Z</updated>
  <author>
    <name>The Secretariat of the ISO 4217 Maintenance Agency</name>
  </author>
  <entry>
    <id>{url}#{updated:%Y-%m-%d}</id>
    <title>ISO 4217 &#x2014; Amendment: {updated:%Y-%m-%d}</title>
    <link href="http://www.iso.org/iso/home/standards/currency_codes.htm"
          type="text/html" />
    <link href="http://www.currency-iso.org/dam/downloads/lists/list_one.xml"
          type="text/xml" />
    <updated>{updated:%Y-%m-%d}T00:00:00Z</updated>
    <summary>ISO 4217 &#x2014; Amendment: {updated:%Y-%m-%d}</summary>
  </entry>
</feed>
'''.format(updated=updated, url=url),
