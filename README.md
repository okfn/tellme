# TellMe

[![Travis Build Status](https://travis-ci.org/okfn/tellme.svg)](https://travis-ci.org/okfn/tellme)
[![Coverage Status](https://coveralls.io/repos/okfn/tellme/badge.svg)](https://coveralls.io/r/okfn/tellme)

TellMe is a toolkit to create user-facing reports.

Clients write entries to a reporting backend (with an optional schema), and generate output in a number of formats.

Entries are Python dictionaries, and comply with a schema if one is supplied.

A report can be generated from the backend source in several *report formats*.


## Status

Work in progress. It works. Tests pass on Python 2.7, 3.3 and 3.4.

## Get started

Clone into a virtual environment, then:

```
pip install -r requirements/local.txt
```

Run the tests with a coverage report:

```
./tests.sh
```

## Examples

TellMe is used in and developed against [Good Tables](https://github.com/okfn/goodtables).

In addition to the examples below, a working implementation can be seen in the [processors](https://github.com/okfn/goodtables/goodtables/processors/) package.

### Simple report

A simple report example. See tests for more examples.

```
import io
import tempfile
import tellme
from somewhere import normalize_case

report = tellme.Report('file_processor')

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
