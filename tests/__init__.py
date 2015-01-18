import os
import sys
import unittest
import json


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.dirname(TEST_ROOT))
PACKAGE_ROOT = os.path.abspath(os.path.join(REPO_ROOT, 'reporter'))


sys.path.insert(1, REPO_ROOT)
import reporter
from reporter import exceptions


class ReportTest(unittest.TestCase):

    def setUp(self):
        self.report_name = 'report_test'
        self.report_schema = {
            'id': {'type': (int, str)},
            'description': {'type': str}
        }
        self.entries = [
            {'id': 1, 'description': 'First description.'},
            {'id': 2, 'description': 'Second description.'},
            {'id': 3, 'description': 'Third description.'}
        ]

    def test_simple_yaml(self):
        report = reporter.Report(self.report_name)
        report.write(self.entries[0])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['data']), 1)

    def test_simple_sql(self):
        report = reporter.Report(self.report_name, backend='sql')
        report.write(self.entries[0])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['data']), 1)

    def test_with_schema_valid_yaml(self):
        report = reporter.Report(self.report_name, self.report_schema)
        report.write(self.entries[0])
        report.write(self.entries[1])
        report.write(self.entries[2])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['data']), 3)

    def test_with_schema_valid_sql(self):
        report = reporter.Report(self.report_name, self.report_schema,
                                 backend='sql')
        report.write(self.entries[0])
        report.write(self.entries[1])
        report.write(self.entries[2])
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['data']), 3)

    def test_with_schema_invalid_yaml(self):
        report = reporter.Report(self.report_name, self.report_schema)
        invalid_entry = self.entries[0]
        invalid_entry['description'] = 1
        self.assertRaises(exceptions.InvalidEntry, report.write, invalid_entry)

    def test_with_schema_invalid_sql(self):
        report = reporter.Report(self.report_name, self.report_schema,
                                 backend='sql')
        invalid_entry = self.entries[0]
        invalid_entry['description'] = 1
        self.assertRaises(exceptions.InvalidEntry, report.write, invalid_entry)


    def test_generate_json_yaml(self):
        report = reporter.Report(self.report_name, self.report_schema)
        report.write(self.entries[0])
        output = report.generate('json')
        self.assertTrue(json.loads(output))

    def test_generate_json_sql(self):
        report = reporter.Report(self.report_name, self.report_schema,
                                 backend='sql')
        report.write(self.entries[0])
        output = report.generate('json')
        self.assertTrue(json.loads(output))

    def test_multi_write_yaml(self):
        report = reporter.Report(self.report_name, self.report_schema)
        report.multi_write(self.entries)
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['data']), 3)

    def test_multi_write_sql(self):
        report = reporter.Report(self.report_name, self.report_schema,
                                 backend='sql')
        report.multi_write(self.entries)
        output = report.generate()
        self.assertEqual(output['meta']['name'], self.report_name)
        self.assertEqual(len(output['data']), 3)

    def test_merge(self):
        self.assertTrue(False)
