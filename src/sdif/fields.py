import datetime
import enum
from decimal import Decimal
from enum import Enum
from typing import ClassVar, Iterator, Optional, Protocol, cast, runtime_checkable

import attr
from typing_inspect import get_args, is_optional_type

from sdif.time import Time, TimeT

# Model infrastructure


@runtime_checkable
class SdifModel(Protocol):
    # __attrs_attrs__: ClassVar  # pyright can't detect this without the benefit of plugins
    identifier: ClassVar[str]


class FieldType(Enum):
    alpha = enum.auto()
    const = enum.auto()
    code = enum.auto()
    date = enum.auto()
    dec = enum.auto()
    int = enum.auto()
    logical = enum.auto()
    name_ = enum.auto()
    phone = enum.auto()
    postal_code = enum.auto()
    usps = enum.auto()
    ussnum = enum.auto()
    time = enum.auto()


@attr.define(frozen=True)
class FieldMetadata:
    start: int
    len: int
    type: Optional[FieldType]
    m2: bool


def infer_type(attr_type: type, field_meta: FieldMetadata) -> FieldType:
    if field_meta.type:
        return field_meta.type

    if attr_type == str:
        return FieldType.alpha
    if attr_type == int:
        return FieldType.int
    if attr_type in (Time, TimeT):
        return FieldType.time
    if isinstance(attr_type, type) and issubclass(attr_type, Enum):
        return FieldType.code
    if attr_type == datetime.date:
        return FieldType.date
    if attr_type == Decimal:
        return FieldType.dec
    if attr_type == int:
        return FieldType.int
    if attr_type == bool:
        return FieldType.logical
    raise ValueError("Native type not recognized", attr_type)


@attr.define(frozen=True)
class FieldDef:
    name: str
    start: int
    len: int
    m1: bool
    m2: bool
    record_type: FieldType
    model_type: type


def record_fields(cls: type[SdifModel]) -> Iterator[FieldDef]:
    fields = attr.fields(cls)

    yield FieldDef(
        name="identifier",
        start=0,
        len=2,
        m1=True,
        m2=False,
        record_type=FieldType.const,
        model_type=str,
    )

    field: attr.Attribute
    for field in fields:
        if "sdif" not in field.metadata:
            continue
        meta = field.metadata["sdif"]
        assert isinstance(meta, FieldMetadata)

        if is_optional_type(field.type):
            (attr_type,) = [arg for arg in get_args(field.type) if arg != type(None)]
        else:
            attr_type = field.type
        attr_type = cast(type, attr_type)

        m1 = not is_optional_type(field.type)
        yield FieldDef(
            name=field.name,
            start=meta.start,
            len=meta.len,
            m1=m1,
            m2=meta.m2,
            record_type=infer_type(attr_type, meta),
            model_type=attr_type,
        )
