# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import unittest
import json


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.dirname(TEST_ROOT))
PACKAGE_ROOT = os.path.abspath(os.path.join(REPO_ROOT, 'tellme'))


sys.path.insert(1, REPO_ROOT)
import tellme
from tellme import exceptions
from tellme import compat


class ReportTest(unittest.TestCase):

    def setUp(self):
        self.report_name = 'report_test'
        self.report_schema = {
            'id': {'type': (int, compat.str)},
            'description': {'type': compat.str}
        }
        self.entries = [
            {'id': 1, 'description': 'First description.'},
            {'id': 2, 'description': 'Second description.'},
            {'id': 3, 'description': 'Third description.'}
        ]

    def test_simple_yaml(self):
        report = tellme.Report(self.report_name)
        report.write(self.entries[0])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['results']), 1)

    def test_simple_sql(self):
        report = tellme.Report(self.report_name, backend='sql')
        report.write(self.entries[0])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['results']), 1)

    def test_with_schema_valid_yaml(self):
        report = tellme.Report(self.report_name, self.report_schema)
        report.write(self.entries[0])
        report.write(self.entries[1])
        report.write(self.entries[2])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['results']), 3)

    def test_with_schema_valid_sql(self):
        report = tellme.Report(self.report_name, self.report_schema,
                               backend='sql')
        report.write(self.entries[0])
        report.write(self.entries[1])
        report.write(self.entries[2])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['results']), 3)

    def test_with_schema_invalid_yaml(self):
        report = tellme.Report(self.report_name, self.report_schema)
        invalid_entry = self.entries[0]
        invalid_entry['description'] = 1
        self.assertRaises(exceptions.InvalidEntryError, report.write,
                          invalid_entry)

    def test_with_schema_invalid_sql(self):
        report = tellme.Report(self.report_name, self.report_schema,
                               backend='sql')
        invalid_entry = self.entries[0]
        invalid_entry['description'] = 1
        self.assertRaises(exceptions.InvalidEntryError, report.write,
                          invalid_entry)

    def test_generate_json_yaml(self):
        report = tellme.Report(self.report_name, self.report_schema)
        report.write(self.entries[0])
        output = report.generate('json')
        self.assertTrue(json.loads(output))

    def test_generate_json_sql(self):
        report = tellme.Report(self.report_name, self.report_schema,
                               backend='sql')
        report.write(self.entries[0])
        output = report.generate('json')
        self.assertTrue(json.loads(output))

    def test_multi_write_yaml(self):
        report = tellme.Report(self.report_name, self.report_schema)
        report.multi_write(self.entries)
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['results']), 3)

    def test_multi_write_sql(self):
        report = tellme.Report(self.report_name, self.report_schema,
                               backend='sql')
        report.multi_write(self.entries)
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['results']), 3)
