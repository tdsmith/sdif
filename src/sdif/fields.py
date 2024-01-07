import datetime
import enum
from decimal import Decimal
from enum import Enum
from typing import (
    ClassVar,
    Iterator,
    Optional,
    Protocol,
    Union,
    cast,
    runtime_checkable,
)

import attr
from typing_inspect import get_args, is_optional_type, is_union_type

from sdif.time import Time, TimeT

# Model infrastructure


@runtime_checkable
class SdifModel(Protocol):
    # __attrs_attrs__: ClassVar  # pyright can't detect this without the benefit of plugins

    @property
    def identifier(self) -> str:
        ...


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
    override_m1: Optional[bool]


def infer_type(attr_type: type, field_meta: FieldMetadata) -> FieldType:
    if field_meta.type:
        return field_meta.type

    if attr_type == str:
        return FieldType.alpha
    if attr_type == int:
        return FieldType.int
    if attr_type in (Time, TimeT):
        return FieldType.time
    if is_union_type(attr_type) and Time in get_args(attr_type):
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
    """
    m1 describes whether the field is marked m1 in the spec.

    optional describes whether the models can tolerate a None value.
    In strict=True mode, missing values are not tolerated where m1=True.

    In strict=False mode, missing values are tolerated where optional=True, even
    if m1=True.
    """

    name: str
    start: int
    len: int
    m1: bool
    m2: bool
    optional: bool
    record_type: FieldType
    model_type: type


def record_fields(cls: type[SdifModel]) -> Iterator[FieldDef]:
    fields = attr.fields(cls)

    yield FieldDef(
        name="identifier",
        start=1,
        len=2,
        m1=True,
        m2=False,
        optional=False,
        record_type=FieldType.const,
        model_type=str,
    )

    field: attr.Attribute
    for field in fields:
        if "sdif" not in field.metadata:
            continue
        meta = field.metadata["sdif"]
        assert isinstance(meta, FieldMetadata)

        field_is_optional = is_optional_type(field.type)

        if field_is_optional:
            args: list[type] = [arg for arg in get_args(field.type) if arg != type(None)]
            if len(args) == 1:
                (attr_type,) = args
            else:
                attr_type = Union[tuple(args)]  # type: ignore
        else:
            attr_type = field.type
        attr_type = cast(type, attr_type)

        m1 = not field_is_optional
        if meta.override_m1 is not None:
            m1 = meta.override_m1

        yield FieldDef(
            name=field.name,
            start=meta.start,
            len=meta.len,
            m1=m1,
            m2=meta.m2,
            optional=field_is_optional,
            record_type=infer_type(attr_type, meta),
            model_type=attr_type,
        )
