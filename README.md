# sdif

Parser/writer for US Swimming SDIF files.

![Main workflow](https://github.com/tdsmith/sdif/actions/workflows/main.yml/badge.svg?branch=main)
[![PyPI](https://img.shields.io/pypi/v/sdif)](https://pypi.org/project/sdif/)


The format is described in sdifv3.txt,
obtained from https://www.usms.org/admin/sdifv3f.txt,
dated April 28 1998, accessed Feb 12 2023.

> United States Swimming has matured as an organization and
expanded services to individuals and clubs.  To support this
expansion, USS has developed a computer plan. One component is a
standard interchange format for technical data.  Swimming data
must be transmitted among the clubs, Local Swimming Committees
(LSCs), and the USS headquarters office.  Exchanging meet results
is one example, where data from a host club is distributed to
swimmers and clubs using diskettes or modems.  Some LSCs are
compiling swimmer statistics and would retype the data from
printed sheets if electronic transmission were not available.
A standard format promotes easy exchange of data and the
development of new computer programs and services.  The goal is
to preserve the valuable efforts of our volunteers.

## But why?

Swim meet administration uses some incredibly venerable software!
Whatever innovations have visited swimming in the last twenty-five years
have not made much of a mark on the conduct of meets, and a handful
of vendors continue to do the bare minimum to keep their legacy code,
and their legacy data formats, chugging along on new hardware
and modern operating systems.

Most of these legacy data formats have no public documentation, so,
if you'd like to get a bunch of entries into some meet management software,
there aren't many obvious starting points!
They don't accept anything as quotidian as a spreadsheet.

SDIF (SD3) is the proud exception, so here's a library.
SD3 is a single-file data format with multiple record types and optional internal consistency checks.
Each line in the file represents a record, and the fields are specified as fixed-width regions.
It seems intended to represent a sort of flat-file database as much as an interchange format.

You can use this package to make sense of these files,
or construct the records that you need to get data into a meet management tool.

## How do I start?

To read a sd3 file:

```python
with open("my_file.sd3", "rt") as f:
    for record in sdif.records.decode_records(f):
        print(record)
```

To write a sd3 file:

```python
a0 = models.FileDescription(
    organization=models.OrganizationCode.masters,
    sdif_version="V3",
    file_code=models.FileCode.vendor_defined,
    software_name="My Cool Software",
    software_version="v0.0.0",
    contact_name="Joe Bloggs",
    contact_phone="+15555551212",
    file_creation=date.today(),
    submitted_by_lsc=None,
)
with open("my_file.sd3", "w") as f:
    f.write(records.encode_records([a0]))
```

Valid sd3 files must contain at least a FileDescription and a FileTerminator.
See the SDIF specification for more details.

## Other resources

* https://groups.google.com/g/sdif-forum
