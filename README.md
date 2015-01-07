# Reporter

Reporter is a toolkit to create *user-facing reports* from things happening in code.

A Report instance is named, with optional schema and backend configuration.

Client code writes entries to a report backend, which by default is a YAML file.

Entries are Python dictionaries, and comply with a schema if one is supplied.

A Report can be generated from the backend source in several *report formats*.


## Status

This package is work-in-progress.

The code currently runs on Python 3.4 and above. Python 2.7 support is planned.

See the issue tracker for current tasks.

Run the tests from the repo root with:

```
python -m unittest tests
```


## Examples

Reporter is used in and developed against [Tabular Validator](https://github.com/okfn/tabular-validator).

In addition to the examples below, a working implementation can be seen in the [validators](https://github.com/okfn/tabular-validator/tabular_validator/validators/) package.

### Simple report

An Example of a schemaless report, for notifying a user of actions performed on a file.

```
import io
import tempfile
from reporter import Report
from somewhere import normalize_case

report = Report('file_processor')

def clean_data(stream):
    cleaned = tempfile.TemporaryFile()
    for index, line in enumerate(stream):
        result = normalize_case(line)
        if not result == line:
            report_entry = {
                'line': index,
                'description': 'Performed case normalisation on line {0}'.format(index)
            }
            report.write(report_entry)
            line = result
        cleaned.write(line)
    return cleaned

stream = io.open('some/path')
cleaned = clean_data(stream)

# Example report responses
as_dict = report.generate()
as_json = report.generate('json')
as_yaml = report.generate('yaml')

# Example uses
# Pass `as_dict` to the request context in a web view
# Return `as_json` to user over JSON API
# Save `as_yaml` on bucket storage for later retrieval
```

### Report with schema

TODO

```
from reporter import Report, enum_factory

schema = [
    {'id': (int, long)},
    {'description': str},
    {'level': enum_factory(['warning', 'error'])}
]

report = Report('validation', schema)
```

### Merging multiple reports

TODO

```
from reporter import merge

# metareport = merge([list_of_reports])
```
