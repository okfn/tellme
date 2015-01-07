import json
import tempfile
import yaml
from . import encoders
from . import exceptions


class Report(object):

    """Create, manage and output informational reports from Python."""

    REPORT_FORMATS = ('dict', 'json', 'yaml', 'csv', 'html')
    FILE_BACKENDS = ('yaml',)

    def __init__(self, name='report', schema=None, template=None,
                 backend='yaml'):

        self.name = name
        # TODO: Persist `self.meta` in backend
        self.meta = {
            'name': self.name
        }
        self.template = template
        self.schema = schema
        self.backend = backend
        # TODO: Support other backends? file: json, CSV; db: sqlite

        # TODO: Replace tempfile with file on system
        if self.backend in self.FILE_BACKENDS:
            self.storage = tempfile.TemporaryFile(mode='a+t', encoding='utf-8')
            if self.backend == 'yaml':
                # valid YAML documents should start with '---'
                self.storage.write('---\n')
        else:
            raise NotImplementedError

    def write(self, entry):
        """Write an entry to the report."""
        if self._validate_entry(entry):
            return getattr(self, 'write_{0}'.format(self.backend))(entry)
        else:
            raise exceptions.InvalidEntry

    def write_yaml(self, entry):
        """Write an entry to a YAML backend."""
        return self.storage.write(yaml.dump([entry], default_flow_style=False))

    def multi_write(self, entries):
        """Write multiple entries at once."""
        for entry in entries:
            self.write(entry)
        return True

    def read(self):
        return getattr(self, 'read_{0}'.format(self.backend))()

    def read_yaml(self):
        self.storage.seek(0)
        return yaml.load(self.storage.read())

    def close(self):
        """Close the backend storage."""
        if self.backend in self.FILE_BACKENDS:
            return self.close_file()
        else:
            raise NotImplementedError

    def close_file(self):
        """Close backend file."""
        return self.storage.close()

    def generate(self, format='dict'):
        """Generate a report for this validator."""

        if format not in self.REPORT_FORMATS:
            raise ValueError
        else:
            return getattr(self, 'generate_{0}'.format(format))()

    def generate_dict(self):
        return {
            'meta': self.meta,
            'data': self.read()
        }

    def generate_json(self):
        return json.dumps(self.generate_dict(), cls=encoders.ReportJSONEncoder)

    def generate_csv(self):
        raise NotImplementedError

    def _validate_entry(self, entry):
        """Validate the entry against the schema."""

        # TODO: Use JSON Table Schema instead of this simple custom thing :).

        if self.schema is None:
            return True

        for k, v in entry.items():
            if k not in self.schema.keys():
                return False
            if not isinstance(v, self.schema[k]['type']):
                return False

        return True
