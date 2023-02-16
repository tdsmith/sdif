import enum
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, overload

import attr

# Model infrastructure


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
class Field:
    start: int
    len: int
    type: Optional[FieldType]
    m2: bool


def spec(start: int, len: int, type: Optional[FieldType] = None, m2: bool = False):
    return attr.field(metadata=dict(sdif=Field(start=start, len=len, type=type, m2=m2)))


_T = TypeVar("_T")

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
    fields: tuple[attr.Attribute, ...] = attr.fields(model)
    n = len(fields)
    for i in range(n):
        if "sdif" not in fields[i].metadata:
            continue
        a: Field = fields[i].metadata["sdif"]
        al, ar = a.start, a.start + a.len
        for j in range(i + 1, n):
            if "sdif" not in fields[j].metadata:
                continue
            b: Field = fields[j].metadata["sdif"]
            bl, br = b.start, b.start + b.len
            assert al < bl
            assert ar <= bl
    return model
