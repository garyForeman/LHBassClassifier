#! /usr/bin/env python

"""
Author: Gary Foreman
Created: September 18, 2016
This script scrapes image urls, thread titles, user names, and thread
ids from thread links in the For Sale: Bass Guitars forum at
talkbass.com. Information from each thread is saved as a document in a
MongoDB database.
"""

from __future__ import print_function
import sys
import pymongo
from pyquery import PyQuery as pq

sys.path.append('..')
from utilities.utilities import pause_scrape, report_progress

NUM_PAGES = 1
MIN_PAUSE_SECONDS = 5.
MAX_PAUSE_SECONDS = 15.
REPORT_MESSAGE = 'Finished scraping page'
INDEX_TALKBASS = 'http://www.talkbass.com/'
CLASSIFIEDS = "forums/for-sale-bass-guitars.126/"


def get_page_url(i):
    """
    i : integer page number of classified section
    returns : full url path to desired page number
    """

    tb_classified_page = INDEX_TALKBASS + CLASSIFIEDS
    if i > 1:
        tb_classified_page += 'page-' + str(i)

    return tb_classified_page


def get_threads(d):
    """
    d : a PyQuery object containing web page html
    returns: list of thread lis with id beginning with "thread-" and class not
             containing the string 'sticky'
    """

    return d('li[id^="thread-"]:not(.sticky)')


class ThreadDataExtractor(object):
    """
    Extracts thread data to be stored as MongoDB document

    Attributes
    ----------
        thread: lxml.html.HtmlElement
            contains a for sale thread link

        data: dictionary
            contains thread data

    Methods
    -------
        extract_data
            populates fields of data attribute
    """

    def __init__(self, thread):
        self.thread = thread
        self._d = self._parse_thread()
        self.data = {}

    def _parse_thread(self):
        return pq(self.thread)

    def extract_data(self):
        self.data['_id'] = self._extract_thread_id()
        self.data['username'] = self._extract_username()
        self.data['thread_title'] = self._extract_thread_title()
        self.data['image_url'] = self._extract_image_url()
        self.data['post_date'] = self._extract_post_date()

    def _extract_thread_id(self):
        return self._d('li').attr['id'][len('thread-'):]

    def _extract_username(self):
        return self._d('li').attr['data-author']

    def _extract_thread_title(self):
        return self._d('.PreviewTooltip').text()

    def _extract_image_url(self):
        return self._d('.thumb.Av1s.Thumbnail').attr['data-thumbnailurl']

    def _extract_post_date(self):
        post_date = self._d('span.DateTime').text()
        # if thread has been posted within the last week, date is contained
        # elsewhere
        if post_date == '':
            post_date = self._d('abbr.DateTime').attr['data-datestring']

        return post_date


def extract_thread_data(thread_list):
    """
    thread_list: list of lxml.html.HtmlElement containing each for sale thread
                 link
    extracts thread data we want to keep: user name, thread title, thread id,
    and thumbnail image url, and returns a list of documents to be inserted
    into a MongoDB database
    """

    document_list = []

    for thread in thread_list:
        extractor = ThreadDataExtractor(thread)
        extractor.extract_data()
        document_list.append(extractor.data)

    return document_list


def main():
    # Establish connection to MongoDB open on port 27017
    client = pymongo.MongoClient()

    # Access threads database
    db = client.for_sale_bass_guitars

    for i in xrange(1, NUM_PAGES+1):
        tb_classified_page = get_page_url(i)

        # initialize PyQuery
        d = pq(tb_classified_page)

        thread_list = get_threads(d)
        document_list = extract_thread_data(thread_list)
        try:
            _ = db.threads.insert_many(document_list, ordered=False)
        except pymongo.errors.BulkWriteError:
            # Will throw error if _id has already been used. Just want
            # to skip these threads since data has already been written.
            pass

        pause_scrape(MIN_PAUSE_SECONDS, MAX_PAUSE_SECONDS)
        report_progress(i, REPORT_MESSAGE)

    client.close()

if __name__ == '__main__':
    main()
