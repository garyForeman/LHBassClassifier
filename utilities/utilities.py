#! /usr/bin/env python

"""
Author: Gary Foreman
Created: December 28, 2016
Utility functions to be used in various parts of the code base
"""

from __future__ import print_function
import time
import numpy as np

def pause_scrape(min_time, max_time):
    """
    min_time: float, minimum amount of time for which to sleep
    max_time: float, maximum amount of time for which to sleep
    Sleeps for a random amount of time between min_time and max_time seconds.
    """

    seconds = min_time + np.random.random() * (max_time - min_time)
    time.sleep(seconds)

def report_progress(current, message, report_factor=10):
    """
    current: integer, current index
    message: string, progress report message
    report_factor: integer, how often to print progress
    prints message when current is a multiple of report_factor
    """

    is_reportable = current % report_factor == 0
    if is_reportable:
        report = message + ' {0}'.format(current)
        print(report)