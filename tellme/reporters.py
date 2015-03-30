# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import textwrap
import yaml
import dataset
import tabulate
from . import compat
from . import encoders
from . import exceptions


class Report(object):

    """Create, manage and output informational reports from Python."""

    REPORT_FORMATS = ('dict', 'json', 'yaml', 'csv', 'html', 'txt')
    REPORT_BACKENDS = ('sql', 'yaml', 'client')
    FILE_BACKENDS = ('yaml',)

    def __init__(self, name='report', schema=None, limit=None, template=None,
                 backend='yaml', storage_path=None, client_stream=None,
                 post_task=None):

        self.name = name
        self.meta = {
            'name': self.name
        }
        self.template = template
        self.schema = schema
        self.limit = limit
        self.count = 0
        self.post_task = post_task
        self._mutable_report = None
        self.backend = backend
        if self.backend not in self.REPORT_BACKENDS:
            raise ValueError

        elif self.backend == 'client':
            if not hasattr(client_stream, 'writable') or \
                   not client_stream.writable():
                raise ValueError
            else:
                self.storage = client_stream

        elif self.backend in self.FILE_BACKENDS:
            if storage_path:
                self.storage = io.open(storage_path, mode='a+t',
                                       encoding='utf-8')
            else:
                self.storage = compat.NamedTemporaryFile(mode='a+t',
                                                         encoding='utf-8')
            if self.backend == 'yaml':
                # valid YAML documents should start with '---'
                self.storage.write('---\n')

        elif self.backend == 'sql':
            storage_path = storage_path or 'sqlite:///:memory:'
            db = dataset.connect(storage_path)
            self.storage = db['{0}_data'.format(self.name)]

        else:
            raise NotImplementedError

    def full(self):
        """Return boolean if report is full (max. entries)."""

        if self.limit is None:
            return False

        return (self.count >= self.limit)

    def write(self, entry):
        """Write an entry to the report."""
        if not self.full():
            if self._validate_entry(entry):
                self.count += 1
                return getattr(self, 'write_{0}'.format(self.backend))(entry)
            else:
                raise exceptions.InvalidEntryError

    def write_yaml(self, entry):
        """Write an entry to a YAML backend."""
        return self.storage.write(yaml.dump([entry], default_flow_style=False))

    def write_sql(self, entry):
        """Write an entry to an SQLite backend."""
        self.storage.insert(entry)

    def write_client(self, entry):
        """Write an entry to a client stream backend."""
        line = '{0}{1}'.format(json.dumps(entry, ensure_ascii=False), '\n')
        self.storage.write(line)

    def multi_write(self, entries):
        """Write multiple entries at once."""
        for entry in entries:
            self.write(entry)
        return True

    def read(self, only=None, exclude=None):
        return getattr(self, 'read_{0}'.format(self.backend))(only=only, exclude=exclude)

    def read_yaml(self, only=None, exclude=None):
        """Read all data from a YAML backend."""

        self.storage.seek(0)
        _results = yaml.load(self.storage.read()) or []
        if only:
            _results = [{k: v for k, v in r.items() if k in only} for r in _results]
        elif exclude:
            _results = [{k: v for k, v in r.items() if not k in exclude} for r in _results]

        self.storage.seek(0)
        return _results

    def read_sql(self, only=None, exclude=None):
        """Read all data from an SQLite backend."""

        _results = [result for result in self.storage.all()]
        if only:
            _results = [{k: v for k, v in r.items() if k in only} for r in _results]
        elif exclude:
            _results = [{k: v for k, v in r.items() if not k in exclude} for r in _results]

        return _results

    def read_client(self, only=None, exclude=None):
        """Read all data from a client backend."""

        _results = []
        self.storage.seek(0)
        for line in self.storage:
            if only:
                _results.append({k: v for k, v in json.loads(line.rstrip('\n')) if k in only})
            if exclude:
                _results.append({k: v for k, v in json.loads(line.rstrip('\n')) if not k in exclude})
            else:
                _results.append(json.loads(line.rstrip('\n')))

        self.storage.seek(0)
        return _results

    def close(self):
        """Close the backend storage."""
        if self.backend in self.FILE_BACKENDS:
            return self.close_file()

    def close_file(self):
        """Close backend file."""
        return self.storage.close()

    def generate(self, output='dict', only=None, exclude=None):

        """Generate a report.

        Args:
            only (list or tuple): An iterable of field names to filter data out of result objects.
            exclude (list or tuple): An iterable of field names to filter data out of result objects.

            `only` and `exclude` cannot be passed together - doing so will
            raise an exception.

        """

        if output not in self.REPORT_FORMATS:
            raise ValueError

        if only and exclude:
            raise ValueError

        if only is not None and not isinstance(only, (list, tuple, set)):
            raise ValueError

        if exclude is not None and not isinstance(exclude, (list, tuple, set)):
            raise ValueError

        self._mutable_report = {
            'meta': self.meta,
            'results': self.read(only=only, exclude=exclude) or []
        }
        self.close()

        if self.post_task:
            self.post_task(self._mutable_report)

        handler = getattr(self, 'generate_{0}'.format(output))
        return handler(only=only, exclude=exclude)

    def generate_dict(self, only=None, exclude=None):
        """Generate a report as a Python dictionary."""
        return self._mutable_report

    def generate_txt(self, only=None, exclude=None):
        """Generate a report as plain text, using an ASCII table for data."""

        _headers = 'keys'
        _tablefmt = 'grid'
        _report = self.generate_dict(only=only, exclude=exclude)
        _meta = []
        _template = textwrap.dedent("""\
        META.
        {0}

        ###

        RESULTS.
        {1}
        """)
        for k, v in _report['meta'].items():
            _meta.append('{0}: {1}'.format(k.title(), v))
        meta ='\n'.join(_meta)
        if _report['results']:
            results = tabulate.tabulate(_report['results'], headers=_headers, tablefmt=_tablefmt)
        else:
            results = 'No results were generated.'
        return _template.format(meta, results)

    def generate_json(self, only=None, exclude=None):
        """Generate a report as JSON."""
        return json.dumps(self.generate_dict(), cls=encoders.ReportJSONEncoder)

    def generate_csv(self, only=None, exclude=None):
        """Generate a report as CSV."""
        raise NotImplementedError

    def generate_html(self, only=None, exclude=None):
        """Generate a report as HTML."""
        raise NotImplementedError

    def _validate_entry(self, entry):
        """Validate the entry against the schema."""

        if self.schema is None:
            return True

        for k, v in entry.items():
            if k not in self.schema.keys():
                return False
            if not isinstance(v, self.schema[k]['type']):
                return False

        return True
