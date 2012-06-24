# -*- coding: utf-8 -*-
"""
    instrumentation.py
    ~~~~~~~~~~~~~~~~~~~
    Object to gather instrumentation data from the simplenote library
"""
import collections

class Instrumentation(object):
    """ Object to gather instrumentation data from various places
        Its API is mainly inspired by StatsD. It features counters, which are
        just simply counting values for a metric. Timers store a fixed size
        array of timings for a metric and Gauges work analogously.
    """

    def __init__(self, maxlen=100):
        """ constructor for the instrumentation object.

        Arguments:
            maxlen (Integer): length of the metrics deques for timers and
                              gauges

        Returns:
            the instrumentation object
        """
        self.maxlen = maxlen
        self.counters = {}
        self.timers = {}
        self.gauges = {}

    def count(self, metric, value=1):
        """ increment or decrement a counter

        Arguments:
            metric (string): name of the metric to increment
            value (integer): value for the metric (default: 1)

        Returns:
            nothing
        """
        if metric in self.counters:
            self.counters[metric] += value
        else:
            self.counters[metric] = value

    def gauge(self, metric, value):
        """ add a gauge for the given metric name

        Arguments:
            metric (string): name of the metric to add a gauge
            value (integer): value for the metric

        Returns:
            nothing
        """
        if metric in self.gauges:
            self.gauges[metric].append(value)
        else:
            self.gauges[metric] = collections.deque(self.maxlen*[0], self.maxlen)
            self.gauges[metric].append(value)

    def timing(self, metric, value):
        """ add a timing for the given metric name

        Arguments:
            metric (string): name of the metric to add a timing
            value (integer): value for the metric

        Returns:
            nothing
        """
        if metric in self.timers:
            self.timers[metric]["values"].append(value)
        else:
            self.timers[metric] = {}
            self.timers[metric]["values"] = collections.deque(self.maxlen*[0], self.maxlen)
            self.timers[metric]["values"].append(value)

        # calculate some statistics
        self.timers[metric]["mean"] = float(sum(self.timers[metric]["values"]))/float(5)
        self.timers[metric]["upper"] = max(self.timers[metric]["values"])
        self.timers[metric]["lower"] = min(self.timers[metric]["values"])



