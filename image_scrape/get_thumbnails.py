#! /usr/bin/env python

"""
Author: Gary Foreman
Created: August 6, 2016
This script scrapes thumbnail images from thread links in the For Sale: Bass
Guitars forum at talkbass.com
"""

from __future__ import print_function
import csv, os, urllib
import numpy as np
from PIL import Image, ImageOps
from pyquery import PyQuery as pq

DATA_PATH = os.path.join('..', 'data')

INDEX_TALKBASS = 'http://www.talkbass.com/'
IMAGES_TALKBASS = 'http://images'
CLASSIFIEDS = "forums/for-sale-bass-guitars.126/"
NUM_PAGES = 1

def make_data_dir():
    """
    Checks to see whether DATA_PATH exists. If not, creates it.
    """

    if not os.path.isdir(DATA_PATH):
        os.makedirs(DATA_PATH)

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

def filename_from_url(thumbnail_url):
    """
    thumbnail_url : a string with a url to a bass image
    strips filename from the end of thumbnail_url and prepends DATA_PATH 
    """

    return os.path.join(DATA_PATH, thumbnail_url.split('/')[-1])

def download_thumb(thumbnail_url):
    """
    thumbnail_url : a string with a url to a bass image
    Pulls dowm image from thumbnail_url and stores in DATA_DIR
    """

    filename = filename_from_url(thumbnail_url)

    try:
        urllib.urlretrieve(thumbnail_url, filename)
    except IOError:
        #URL is not an image file
        pass

def crop_image(filename):
    """
    filename: a string with the name to a locally stored image file
    Crops image at filename to 128 x 128 pixels and overwrites original
    """

    try:
        img = Image.open(filename)
        img = ImageOps.fit(img, (128, 128), Image.ANTIALIAS)
        img.save(filename)
    except NameError:
        #File does not exist
        pass
    except IOError:
        #Image is corrupted
        os.remove(filename)

def main():
    make_data_dir()
    
    for i in xrange(1, NUM_PAGES+1):
        thumbnail_url_list = []

        tb_classified_page = get_page_url(i)

        #initialize PyQuery
        d = pq(tb_classified_page)

        thumbnail_url_list.extend(get_thumb_urls(d))

        map(download_thumb, thumbnail_url_list)
        filename_list = map(filename_from_url, thumbnail_url_list)
        map(crop_image, filename_list)

        print("page", i, "finished")

if __name__ == "__main__":
    main()