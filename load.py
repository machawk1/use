#!/usr/bin/env python3

import os
import csv
import sys
import gzip
import json
import warcio
import logging
import datetime
import requests
import urllib.parse
import urllib.request

from jmespath import search as q

# These are the web archive host names that we will look for
#
# TODO: should we add IPFS gateway URLs:
# https://ipfs.github.io/public-gateway-checker/?

archive_hosts = {
    "web.archive.org":                "InternetArchive",
    "wayback.archive.org":            "InternetArchive",
    "archive.is":                     "ArchiveToday",
    "archive.vn":                     "ArchiveToday",
    "archive.today":                  "ArchiveToday",
    "www.webcitation.org":            "Webcitation",
    "webcitation.org":                "Webcitation",
    "perma.cc":                       "PermaCC",
    "webrecorder.io":                 "Webrecorder",
    "conifer.rhizome.org":            "Webrecorder",
    "webcache.googleusercontent.com": "Google"
}

def main():
    logging.basicConfig(
        filename='load.log',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    snap_id = sys.argv[1]
    cols = [
        "source_url",
        "source_host",
        "archive_url",
        "archive_service",
        "link_text",
        "path",
        "link_count",
        "warc",
        "offset",
        "inflated_length",
        "deflated_length"
    ]
    csv_file = snap_id + '.csv'
    out = csv.DictWriter(open(csv_file, 'w'), fieldnames=cols)
    out.writeheader()

    logging.info('writing csv file %s', csv_file)
    for wat_url in get_wats(snap_id):
        logging.info('processing wat %s', wat_url)
        for link_data in process_wat(wat_url):
            out.writerow(link_data)
    out.close()

def get_wats(snap_id):
    url = "https://commoncrawl.s3.amazonaws.com/crawl-data/" + snap_id + "/wat.paths.gz"
    path = localize(url)
    for line in gzip.open(path, 'rt'):
        line = line.strip()
        url = 'https://commoncrawl.s3.amazonaws.com/' + line
        yield url

    os.remove(path)

def process_wat(wat_url):
    start = datetime.datetime.now()
    path = localize(wat_url)
    for record in warcio.ArchiveIterator(open(path, 'rb')):
        if record.rec_headers.get_header('Content-Type') == "application/json":
            yield from extract_archive_links(record)
    logging.info('removing %s', path)
    os.remove(path)
    elapsed = datetime.datetime.now() - start
    logging.info('finished %s: %s seconds', wat_url, elapsed.total_seconds())

def extract_archive_links(record):
    wat = json.loads(record.raw_stream.read())
    source_url = q('Envelope."WARC-Header-Metadata"."WARC-Target-URI"', wat)
    links = q('Envelope."Payload-Metadata"."HTTP-Response-Metadata"."HTML-Metadata".Links', wat) or []

    # count of url links 
    link_count = len(list(filter(lambda l: 'url' in l, links)))

    for link in links:
        url = link.get('url')

        # only return links to a known web archive
        archive_service = get_archive_service(url)
        if not archive_service:
            continue

        yield {
            "source_url":       source_url,
            "source_host":      get_host(source_url),
            "archive_url":      url,
            "archive_service":  archive_service,
            "link_text":        link.get('text'),
            "path":             link.get('path'),
            "link_count":       link_count,
            "warc":             q('Container.Filename', wat),
            "offset":           q('Container.Offset', wat),
            "inflated_length":  q('Container."Gzip-Metadata"."Inflated-Length"', wat),
            "deflated_length":  q('Container."Gzip-Metadata"."Deflated-Length"', wat),
        }

def get_archive_service(url):
    return archive_hosts.get(get_host(url))

def get_host(url):
    try:
        u = urllib.parse.urlparse(url)
        return u.netloc
    except Exception as e:
        logging.error('unable to parse url %s: %s', url, e)
        return None

def localize(url):
    path, headers = urllib.request.urlretrieve(url)
    logging.info('downloaded %s to %s', url, path)
    return path

if __name__ == "__main__":
    main()
