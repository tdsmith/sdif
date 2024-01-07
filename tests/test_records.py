from datetime import date
from decimal import Decimal
from typing import Any

import pytest

import sdif.models as models
from sdif.fields import FieldDef, FieldType
from sdif.records import decode_records, decode_value, encode_records, encode_value
from sdif.time import Time, TimeCode


@pytest.mark.parametrize(
    ("field_type", "len", "value", "expected"),
    [
        (FieldType.alpha, 8, "abc", "abc     "),
        (FieldType.alpha, 8, "123", "     123"),
        (FieldType.alpha, 8, None, "        "),
        (FieldType.const, 2, "A0", "A0"),
        (FieldType.const, 8, "A0", "A0      "),
        (FieldType.code, 2, None, "  "),
        (FieldType.code, 2, models.FileCode.meet_registrations, "01"),
        (FieldType.code, 8, models.FileCode.meet_registrations, "01      "),
        (FieldType.date, 8, date(2000, 2, 29), "02292000"),
        (FieldType.date, 8, None, "        "),
        (FieldType.dec, 4, None, "    "),
        (FieldType.dec, 8, Decimal("1.234"), "   1.234"),
        (FieldType.int, 4, 1234, "1234"),
        (FieldType.int, 8, 1234, "    1234"),
        (FieldType.logical, 1, True, "T"),
        (FieldType.logical, 1, False, "F"),
        (FieldType.logical, 1, None, " "),
        (FieldType.name_, 12, None, "            "),
        (FieldType.name_, 12, "Smith, Tim", "Smith, Tim  "),
        (FieldType.phone, 12, None, " " * 12),
        (FieldType.phone, 16, "123-456-7890", "123-456-7890    "),
        (FieldType.postal_code, 8, "01234", "01234   "),
        (FieldType.postal_code, 8, "V6E 1T7", "V6E 1T7 "),
        (FieldType.usps, 2, None, "  "),
        (FieldType.usps, 2, "BC", "BC"),
        (FieldType.ussnum, 14, None, " " * 14),
        (FieldType.ussnum, 14, "011553CATADURA", "011553CATADURA"),
        (FieldType.time, 8, Time.from_str("12:00.00"), "12:00.00"),
        (FieldType.time, 8, Time.from_str("12:34.56"), "12:34.56"),
        (FieldType.time, 8, Time.from_str("34.56"), "   34.56"),
        (FieldType.time, 8, Time.from_str("1.23"), "   01.23"),
        (FieldType.time, 8, TimeCode.did_not_finish, "DNF     "),
    ],
)
def test_round_trip_value(field_type: FieldType, len: int, value: Any, expected: str):
    """Test round-trip value conversion.
    These values should all convert back to a form equivalent to the original representation.
    """
    field_def = FieldDef(
        "bogus_field",
        start=0,
        len=len,
        m1=False,
        m2=False,
        optional=True,
        record_type=field_type,
        model_type=type(value),
    )
    assert encode_value(field_def, value, strict=True) == expected
    assert decode_value(field_def, expected, strict=True) == value


@pytest.mark.parametrize(
    ("field_type", "len", "value", "expected", "roundtrip"),
    [
        (FieldType.dec, 8, Decimal("1.23456789"), "1.234567", Decimal("1.234567")),
        (FieldType.usps, 2, "va", "VA", "VA"),
    ],
)
def test_round_trip_ish_value(
    field_type: FieldType, len: int, value: Any, expected: str, roundtrip: str
):
    """Test round-trip value conversion.
    These values suffer some form of lossy conversion, but do not throw errors.
    """
    field_def = FieldDef(
        "bogus_field",
        start=0,
        len=len,
        m1=False,
        m2=False,
        optional=True,
        record_type=field_type,
        model_type=type(value),
    )
    assert encode_value(field_def, value, strict=True) == expected
    assert decode_value(field_def, expected, strict=True) == roundtrip


def test_round_trip_record():
    m = models.FileDescription(
        organization=models.OrganizationCode.masters,
        sdif_version="V3",
        file_code=models.FileCode.vendor_defined,
        software_name="hi, mom",
        software_version="beta",
        contact_name="Joe Bloggs",
        contact_phone="+15555551212",
        file_creation=date.today(),
        submitted_by_lsc=None,
    )
    serialized = encode_records([m])
    print(repr(serialized))
    (deserialized,) = decode_records(serialized)
    assert m == deserialized


def test_round_trip_hytek_signon():
    orig = "A02V3      02                              Hy-Tek, Ltd         WMM 8.0Ea Hy-Tek, Ltd     -USS866-456-511102182023                                               "
    (record,) = decode_records([orig])
    serialized = encode_records([record])
    assert orig == serialized
