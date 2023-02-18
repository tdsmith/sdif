from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Final, get_args
from typing_extensions import assert_never

import sdif.fields as fields
from sdif.fields import FieldDef, FieldType
from sdif.time import Time, TimeT


RECORD_CONTENT_LEN: Final = 160
RECORD_SEP: Final = "\r\n"


def encode_value(field: FieldDef, value: Any) -> str:
    if value is None:
        if field.m1:
            raise ValueError(f"No value provided for mandatory field {field=}")
        return " " * field.len

    field_type = field.type

    # "Alpha fields containing only numeric data should be right justified."
    if field_type == fields.FieldType.alpha:
        assert isinstance(value, str)
        if value.isnumeric():
            value = int(value)
            field_type = FieldType.int

    if field_type == FieldType.usps:
        assert isinstance(value, str)
        value = value.upper()

    if field_type in (
        FieldType.alpha,
        FieldType.const,
        FieldType.name_,
        FieldType.phone,
        FieldType.postal_code,
        FieldType.usps,
        FieldType.ussnum,
    ):
        value = "" if value is None else str(value)
        if len(value) > field.len:
            raise ValueError(f"Value is too wide to encode; {field.len=}, {value=}")
        return f"{{: <{field.len}s}}".format(value)

    if field_type == FieldType.code:
        assert isinstance(value, Enum)
        assert len(value.value) <= field.len
        return f"{{: <{field.len}s}}".format(value.value)

    if field_type == FieldType.date:
        assert isinstance(value, date)
        assert field.len == 8
        return value.strftime("%m%d%Y")

    if field_type == FieldType.dec:
        assert isinstance(value, Decimal)
        value = str(value)[: field.len]
        return f"{{: >{field.len}s}}".format(value)

    if field_type == FieldType.int:
        value = int(value)
        assert value >= 0
        formatted = f"{{: >{field.len}d}}".format(value)
        if len(formatted) > field.len:
            raise ValueError(f"Value is too wide to encode; {field.len=}, {value=}")
        return formatted

    if field_type == FieldType.logical:
        assert isinstance(value, bool)
        assert field.len == 1
        if value is True:
            return "T"
        if value is False:
            return "F"
        assert_never(value)

    if field_type == FieldType.time:
        assert isinstance(value, get_args(TimeT))
        if isinstance(value, Time):
            return f"{{: >{field.len}s}}".format(value.format())
        elif isinstance(value, Enum):
            return f"{{: <{field.len}s}}".format(value.value)
        else:
            raise TypeError("Unexpected TimeT")

    assert_never(field_type)
