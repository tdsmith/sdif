import datetime
import enum
from decimal import Decimal
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Iterator,
    Optional,
    Protocol,
    TypeVar,
    overload,
)

import attr
from typing_inspect import get_args, is_optional_type

from sdif.time import Time, TimeT

# Model infrastructure


class SdifModel(Protocol):
    __attrs_attrs__: ClassVar
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


def infer_type(attribute: attr.Attribute) -> FieldType:
    if "sdif" not in attribute.metadata:
        raise TypeError("Not an SDIF spec field")
    field: FieldMetadata = attribute.metadata["sdif"]
    if field.type:
        return field.type

    if is_optional_type(attribute.type):
        (attr_type,) = [arg for arg in get_args(attribute.type) if arg != type(None)]
    else:
        attr_type = attribute.type

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


def spec(start: int, len: int, type: Optional[FieldType] = None, m2: bool = False):
    return attr.field(metadata=dict(sdif=FieldMetadata(start=start, len=len, type=type, m2=m2)))


@attr.define(frozen=True)
class FieldDef:
    name: str
    start: int
    len: int
    m1: bool
    m2: bool
    type: FieldType


def record_fields(cls: type[SdifModel]) -> Iterator[FieldDef]:
    fields = attr.fields(cls)

    yield FieldDef(
        name="identifier",
        start=0,
        len=2,
        m1=True,
        m2=False,
        type=FieldType.const,
    )

    field: attr.Attribute
    for field in fields:
        if "sdif" not in field.metadata:
            continue
        meta = field.metadata["sdif"]
        assert isinstance(meta, FieldMetadata)
        m1 = not is_optional_type(field.type)
        yield FieldDef(
            name=field.name,
            start=meta.start,
            len=meta.len,
            m1=m1,
            m2=meta.m2,
            type=infer_type(field),
        )


if TYPE_CHECKING:
    from attr import _C, __dataclass_transform__, _FieldTransformer, _OnSetAttrArgType

    @overload
    @__dataclass_transform__(field_descriptors=(attr.attrib, attr.field, spec))
    def model(
        maybe_cls: _C,
        *,
        these: Optional[dict[str, Any]] = ...,
        repr: bool = ...,
        unsafe_hash: Optional[bool] = ...,
        hash: Optional[bool] = ...,
        init: bool = ...,
        slots: bool = ...,
        frozen: bool = ...,
        weakref_slot: bool = ...,
        str: bool = ...,
        auto_attribs: bool = ...,
        kw_only: bool = ...,
        cache_hash: bool = ...,
        auto_exc: bool = ...,
        eq: Optional[bool] = ...,
        order: Optional[bool] = ...,
        auto_detect: bool = ...,
        getstate_setstate: Optional[bool] = ...,
        on_setattr: Optional[_OnSetAttrArgType] = ...,
        field_transformer: Optional[_FieldTransformer] = ...,
        match_args: bool = ...,
    ) -> _C:
        ...

    @overload
    @__dataclass_transform__(field_descriptors=(attr.attrib, attr.field, spec))
    def model(
        maybe_cls: None = ...,
        *,
        these: Optional[dict[str, Any]] = ...,
        repr: bool = ...,
        unsafe_hash: Optional[bool] = ...,
        hash: Optional[bool] = ...,
        init: bool = ...,
        slots: bool = ...,
        frozen: bool = ...,
        weakref_slot: bool = ...,
        str: bool = ...,
        auto_attribs: bool = ...,
        kw_only: bool = ...,
        cache_hash: bool = ...,
        auto_exc: bool = ...,
        eq: Optional[bool] = ...,
        order: Optional[bool] = ...,
        auto_detect: bool = ...,
        getstate_setstate: Optional[bool] = ...,
        on_setattr: Optional[_OnSetAttrArgType] = ...,
        field_transformer: Optional[_FieldTransformer] = ...,
        match_args: bool = ...,
    ) -> Callable[[_C], _C]:
        ...


def model(*args, **kwargs):
    return attr.define(*args, frozen=True, kw_only=True, **kwargs)


A = TypeVar("A", bound=attr.AttrsInstance)


def validate_model(model: type[A]) -> type[A]:
    attr.resolve_types(model)
    fields: tuple[attr.Attribute, ...] = attr.fields(model)
    indices = []
    for field in fields:
        if "sdif" not in field.metadata:
            continue
        spec: FieldMetadata = field.metadata["sdif"]
        indices.append(spec.start)
        indices.append(spec.start + spec.len)
    # Assert field specs are sorted and non-overlapping
    assert indices == sorted(indices)
    return model
