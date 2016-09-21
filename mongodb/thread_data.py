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
import csv, os, urllib
import numpy as np
from pymongo import MongoClient
from pyquery import PyQuery as pq

INDEX_TALKBASS = 'http://www.talkbass.com/'
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
        document_list.append({'_id': thread_id,
                              'username': username,
                              'thread_title': thread_title,
                              'image_url': image_url})

    return document_list

if __name__ == '__main__':
    #Establish connection to MongoDB open on port 27017
    client = MongoClient()

    #Access threads database
    db = client.threads


    for i in xrange(1, NUM_PAGES+1):
        tb_classified_page = get_page_url(i)

        #initialize PyQuery
        d = pq(tb_classified_page)

        thread_list = get_threads(d)
        document_list = extract_thread_data(thread_list)
        for document in document_list:
            print(document)