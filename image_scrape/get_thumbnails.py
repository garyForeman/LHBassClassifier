#! /usr/bin/env python

"""
Author: Gary Foreman
Created: August 6, 2016
This script scrapes thumbnail images from thread links in the For Sale: Bass
Guitars forum at talkbass.com
"""

from __future__ import print_function
import csv
import numpy as np
from pyquery import PyQuery as pq

INDEX_TALKBASS = 'http://www.talkbass.com/'
IMAGES_TALKBASS = 'http://images'
CLASSIFIEDS = "forums/for-sale-bass-guitars.126/"
NUM_PAGES = 1

def get_page_url(i):
    """
    i : integer page number of classified section
    returns : full url path to desired page number
    """

    tb_classified_page = INDEX_TALKBASS + CLASSIFIEDS
    if i > 1: tb_classified_page += 'page-' + str(i)

    return tb_classified_page

def get_thumb_urls(d):
    """
    d : a PyQuery object containing web page html
    returns: list of thumbnail urls
    """

    thumbnail_url_list = []
    for threadlink in d('.thumb.Av1s.Thumbnail').items():
        thumbnail_url_list.append(threadlink.attr['data-thumbnailurl'])

    return thumbnail_url_list

def main():
    thumbnail_url_list = []

    for i in xrange(1, NUM_PAGES+1):
        tb_classified_page = get_page_url(i)

        #initialize PyQuery
        d = pq(tb_classified_page)

        thumbnail_url_list.extend(get_thumb_urls(d))

        print("page", i, "finished")

if __name__ == "__main__":
    main()