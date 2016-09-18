#! /usr/bin/env python

"""
Author: Gary Foreman
Created: September 18, 2016
This script scrapes image urls, thread titles, user names, and thread
ids from thread links in the For Sale: Bass Guitars forum at
talkbass.com. Information from each thread is saved as a document in a 
MongoDB data base.
"""

from __future__ import print_function
import csv, os, urllib
import numpy as np
from pymongo import MongoClient
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

def get_threads(d):
    """
    d : a PyQuery object containing web page html
    returns: list of thread lis with id beginning with "thread-" class not
             containing the string 'sticky'
    """

    return d('li[id^="thread-"]:not(.sticky)')

def extract_thread_data(thread_list):
    """
    thread_list: list of lxml.html.HtmlElement containing each for sale thread
                 link
    extracts thread data we want to keep: user name, thread title, thread id,
    and thumbnail image url
    """

    for thread in thread_list:
        #parse thread using PyQuery
        d = pq(thread)
        print("Thread id:", d('li').attr['id'][len("thread-"):])
        print("User name:", d('li').attr['data-author'])
        print("Thread title:", d('.PreviewTooltip').text())
        print("Image url:", d('.thumb.Av1s.Thumbnail').attr['data-thumbnailurl'])

if __name__ == '__main__':
    #Establish connection to MongoDB open on port 27017
    #client = MongoClient()

    #Access threads data base
    #db = client.threads


    for i in xrange(1, NUM_PAGES+1):
        tb_classified_page = get_page_url(i)

        #initialize PyQuery
        d = pq(tb_classified_page)

        thread_list = get_threads(d)
        extract_thread_data(thread_list)










