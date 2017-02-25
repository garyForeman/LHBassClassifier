#! /usr/bin/env python

"""
Author: Gary Foreman
Created: August 6, 2016
This script scrapes thumbnail images from thread links in the For Sale: Bass
Guitars forum at talkbass.com
"""

from __future__ import print_function
from glob import glob
import os
import sys
import urllib
from PIL import Image, ImageOps
import pymongo

sys.path.append('..')
from utilities.utilities import pause_scrape, report_progress

MIN_PAUSE_SECONDS = 0.15
MAX_PAUSE_SECONDS = 0.5
REPORT_MESSAGE = 'Scraped image'
REPORT_FREQUENCY = 300
DATA_PATH = os.path.join('..', 'data', 'images')


def make_data_dir():
    """
    Checks to see whether DATA_PATH exists. If not, creates it.
    """

    if not os.path.isdir(DATA_PATH):
        os.makedirs(DATA_PATH)


def filename_from_url(thumbnail_url):
    """
    thumbnail_url : a string with a url to a bass image
    Strips filename from the end of thumbnail_url and prepends DATA_PATH.
    Also ensures the file extension is jpg
    """

    filename = thumbnail_url.strip('/').split('/')[-1]
    basename, ext = os.path.splitext(filename)
    return os.path.join(DATA_PATH, basename + '.jpg')


def download_thumb(thumbnail_url):
    """
    thumbnail_url : a string with a url to a bass image
    Pulls dowm image from thumbnail_url and stores in DATA_DIR
    """

    filename = filename_from_url(thumbnail_url)

    try:
        urllib.urlretrieve(thumbnail_url, filename)
    except IOError:
        # URL is not an image file
        pass
    except UnicodeError:
        # URL contains non-ASCII characters
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
        # File does not exist
        pass
    except IOError:
        # Image is corrupted
        try:
            os.remove(filename)
        except OSError:
            # Filename is too long
            pass


def main():
    make_data_dir()

    # Establish connection to MongoDB open on port 27017
    client = pymongo.MongoClient()

    # Access threads database
    db = client.for_sale_bass_guitars

    # Get database documents
    cursor = db.threads.find()

    # Get list of images that have already been scraped
    scraped_image_list = glob(os.path.join(DATA_PATH, '*.jpg'))

    thumbnail_url_list = []
    for document in cursor:
        thumbnail_url = document[u'image_url']
        try:
            filename = filename_from_url(thumbnail_url)
            if filename not in scraped_image_list:
                thumbnail_url_list.append(thumbnail_url)
        except AttributeError:
            # thread has no associated thumbnail
            pass

    client.close()

    thumbnail_count = 1
    for thumbnail_url in thumbnail_url_list:
        download_thumb(thumbnail_url)
        filename = filename_from_url(thumbnail_url)
        crop_image(filename)

        pause_scrape(MIN_PAUSE_SECONDS, MAX_PAUSE_SECONDS)
        report_progress(thumbnail_count, REPORT_MESSAGE, REPORT_FREQUENCY)
        thumbnail_count += 1

if __name__ == "__main__":
    main()
