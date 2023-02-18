from datetime import date
from decimal import Decimal
from typing import Any

import pytest

import sdif.models as models
from sdif.fields import FieldType, FieldDef
from sdif.records import encode_value
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
        (FieldType.dec, 8, Decimal("1.23456789"), "1.234567"),
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
        (FieldType.usps, 2, "va", "VA"),
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
def test_encode_value(field_type: FieldType, len: int, value: Any, expected: str):
    field_def = FieldDef("bogus_field", start=0, len=len, m1=False, m2=False, type=field_type)
    assert encode_value(field_def, value) == expected
