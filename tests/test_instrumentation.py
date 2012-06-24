# -*- coding: utf-8 -*-
import unittest
import os
import sys
sys.path.append(os.getcwd())
from simplenote.instrumentation import Instrumentation

class TestSimplenote(unittest.TestCase):

    def setUp(self):
        self.i = Instrumentation(5)

    def tearDown(self):
        del self.i

    def test_counters(self):
        self.i.count("foobar", 5)
        self.assertEqual(5, self.i.counters["foobar"])

    def test_multiple_counters(self):
        self.i.count("foobar", 5)
        self.i.count("foobar", 3)
        self.assertEqual(8, self.i.counters["foobar"])

    def test_gauge(self):
        self.i.gauge("foobar", 3)
        self.assertEqual(5, len(self.i.gauges["foobar"]))
        self.assertEqual(3, self.i.gauges["foobar"][-1])

    def test_multiple_gauges(self):
        self.i.gauge("foobar", 4)
        self.i.gauge("foobar", 3)
        self.assertEqual(5, len(self.i.gauges["foobar"]))
        self.assertEqual(3, self.i.gauges["foobar"][-1])
        self.assertEqual(4, self.i.gauges["foobar"][-2])

    def test_timing(self):
        self.i.timing("foobar", 3)
        self.assertEqual(5, len(self.i.timers["foobar"]["values"]))
        self.assertEqual(3, self.i.timers["foobar"]["values"][-1])
        self.assertEqual(3, self.i.timers["foobar"]["upper"])
        self.assertEqual(0, self.i.timers["foobar"]["lower"])
        self.assertAlmostEqual(0.6, self.i.timers["foobar"]["mean"], 1)

    def test_multiple_timings(self):
        self.i.timing("foobar", 3)
        self.i.timing("foobar", 3)
        self.assertEqual(5, len(self.i.timers["foobar"]["values"]))
        self.assertEqual(3, self.i.timers["foobar"]["values"][-1])
        self.assertEqual(3, self.i.timers["foobar"]["upper"])
        self.assertEqual(0, self.i.timers["foobar"]["lower"])
        self.assertAlmostEqual(1.2, self.i.timers["foobar"]["mean"], 1)


if __name__ == '__main__':
    unittest.main()


