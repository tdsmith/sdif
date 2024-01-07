from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Final, Iterable, TypeVar, get_args

from typing_extensions import assert_never

import sdif.fields as fields
import sdif.model_meta as model_meta
from sdif.fields import FieldDef, FieldType, SdifModel
from sdif.time import Time, TimeCode, TimeT

RECORD_CONTENT_LEN: Final = 160
RECORD_SEP: Final = "\r\n"


def encode_value(field: FieldDef, value: Any, strict: bool) -> str:
    if value is None:
        if (strict and field.m1) or (not strict and not field.optional):
            raise ValueError(f"No value provided for mandatory field {field=}")
        return " " * field.len

    field_type = field.record_type

    # "Alpha fields containing only numeric data should be right justified."
    if field_type == fields.FieldType.alpha:
        str_value = str(value)
        if str_value.isnumeric():
            value = int(str_value)
            field_type = FieldType.int

    if field_type == FieldType.usps:
        assert isinstance(value, str), f"{field=} {value=}"
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
        value = str(value)
        if len(value) > field.len:
            raise ValueError(f"Value is too wide to encode; {field.len=}, {value=}")
        return f"{{: <{field.len}s}}".format(value)

    if field_type == FieldType.code:
        assert isinstance(value, Enum), f"{field=} {value=}"
        assert len(value.value) <= field.len
        return f"{{: <{field.len}s}}".format(value.value)

    if field_type == FieldType.date:
        assert isinstance(value, date), f"{field=} {value=}"
        assert field.len == 8
        return value.strftime("%m%d%Y")

    if field_type == FieldType.dec:
        assert isinstance(value, Decimal), f"{field=} {value=}"
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
        assert isinstance(value, bool), f"{field=} {value=}"
        assert field.len == 1
        if value is True:
            return "T"
        if value is False:
            return "F"
        assert_never(value)

    if field_type == FieldType.time:
        assert isinstance(value, get_args(TimeT)), f"{field=} {value=}"
        if isinstance(value, Time):
            return f"{{: >{field.len}s}}".format(value.format())
        elif isinstance(value, Enum):
            return f"{{: <{field.len}s}}".format(value.value)
        else:
            raise TypeError("Unexpected TimeT")

    assert_never(field_type)


def encode_record(record: fields.SdifModel, strict: bool) -> str:
    buf = [" "] * RECORD_CONTENT_LEN
    for field in fields.record_fields(type(record)):
        value = getattr(record, field.name)
        encoded = encode_value(field, value, strict)
        assert len(encoded) == field.len
        buf[field.start - 1 : field.start - 1 + field.len] = encoded
    return "".join(buf)


def encode_records(records: Iterable[fields.SdifModel], strict: bool = False) -> str:
    return RECORD_SEP.join(encode_record(i, strict) for i in records)


def decode_value(field: FieldDef, value: str, strict: bool) -> Any:
    field_type = field.record_type
    stripped = value.strip()
    if stripped == "":
        if (strict and field.m1) or (not strict and not field.optional):
            raise ValueError(f"Blank value for mandatory field; {field=}")
        return None
    if field_type in (
        FieldType.alpha,
        FieldType.const,
        FieldType.name_,
        FieldType.phone,
        FieldType.postal_code,
        FieldType.usps,
        FieldType.ussnum,
    ):
        return stripped

    if field_type == FieldType.code:
        enum = field.model_type
        return enum(stripped)

    if field_type == FieldType.date:
        m, d, y = value[:2], value[2:4], value[4:]
        return date(int(y), int(m), int(d))

    if field_type == FieldType.dec:
        return Decimal(stripped)

    if field_type == FieldType.int:
        return int(stripped)

    if field_type == FieldType.logical:
        if stripped == "T":
            return True
        if stripped == "F":
            return False
        raise ValueError(f"Can't convert to logical; {value=}")

    if field_type == FieldType.time:
        try:
            return Time.from_str(stripped)
        except Exception:
            pass

        try:
            return TimeCode(stripped)
        except Exception:
            pass

        raise ValueError(f"Can't interpret time; {value=}")

    assert_never(field_type)


M = TypeVar("M", bound=fields.SdifModel)


def decode_record(record: str, record_type: type[M], strict: bool) -> M:
    kwargs = {}
    for field in fields.record_fields(record_type):
        if field.name == "identifier":
            continue
        value = record[field.start - 1 : field.start - 1 + field.len]
        decoded = decode_value(field, value, strict)
        kwargs[field.name] = decoded
    return record_type(**kwargs)


def decode_records(records: Iterable[str], strict: bool = False) -> Iterable[SdifModel]:
    if isinstance(records, str):
        records = records.split(RECORD_SEP)
    for record in records:
        cls = model_meta.REGISTERED_MODELS[record[:2]]
        yield decode_record(record, cls, strict)
