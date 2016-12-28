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
import time
import numpy as np
import pymongo
from pyquery import PyQuery as pq

INDEX_TALKBASS = 'http://www.talkbass.com/'
CLASSIFIEDS = "forums/for-sale-bass-guitars.126/"
NUM_PAGES = 400

def get_page_url(i):
    """
    i : integer page number of classified section
    returns : full url path to desired page number
    """

    tb_classified_page = INDEX_TALKBASS + CLASSIFIEDS
    if i > 1: tb_classified_page += 'page-' + str(i)

    return tb_classified_page

def get_threads(d):
    """
    d : a PyQuery object containing web page html
    returns: list of thread lis with id beginning with "thread-" and class not
             containing the string 'sticky'
    """

    return d('li[id^="thread-"]:not(.sticky)')

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
        #parse thread using PyQuery
        d = pq(thread)

        thread_id = d('li').attr['id'][len('thread-'):]
        username = d('li').attr['data-author']
        thread_title = d('.PreviewTooltip').text()
        image_url = d('.thumb.Av1s.Thumbnail').attr['data-thumbnailurl']
        post_date = d('span.DateTime').text()
        #if thread has been posted within the last week, date is contained
        #elsewhere
        if post_date == '':
            post_date = d('abbr.DateTime').attr['data-datestring']

        document_list.append({'_id': thread_id, 'username': username,
                              'thread_title': thread_title,
                              'image_url': image_url, 'post_date': post_date})

    return document_list

def pause_scrape():
    """
    Sleeps for a random amount of time between 5 and 15 seconds.
    """

    seconds = 5. + np.random.random() * 10.
    time.sleep(seconds)

def report_progress(current_page, report_page_factor=10):
    """
    current_page: integer, last page number of thread data scraped
    report_page_factor: integer, how often to print progress
    prints scraping progress if current_page is a factor if report_page_factor
    """

    is_reportable = current_page % report_page_factor == 0
    if is_reportable:
        report = 'Finished scraping page {0}'.format(current_page)
        print(report)

def main():
    #Establish connection to MongoDB open on port 27017
    client = pymongo.MongoClient()

    #Access threads database
    db = client.for_sale_bass_guitars

    for i in xrange(1, NUM_PAGES+1):
        tb_classified_page = get_page_url(i)

        #initialize PyQuery
        d = pq(tb_classified_page)

        thread_list = get_threads(d)
        document_list = extract_thread_data(thread_list)
        try:
            result = db.threads.insert_many(document_list, ordered=False)
        except pymongo.errors.BulkWriteError:
            # Will throw error if _id has already been used. Just want
            # to skip these threads since data has already been written.
            pass

        pause_scrape()
        report_progress(i)

    client.close()

if __name__ == '__main__':
    main()
