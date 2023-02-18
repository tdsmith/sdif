from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
    overload,
)


import attr

from sdif.fields import FieldType, FieldMetadata, SdifModel


REGISTERED_MODELS: dict[str, type[SdifModel]] = {}


def spec(start: int, len: int, type: Optional[FieldType] = None, m2: bool = False):
    return attr.field(metadata=dict(sdif=FieldMetadata(start=start, len=len, type=type, m2=m2)))


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
    def inner(cls):
        return model(cls, **kwargs)

    if not args:
        return inner

    model_cls = attr.define(*args, **kwargs)
    validate_model(model_cls)
    assert model_cls.identifier not in REGISTERED_MODELS
    REGISTERED_MODELS[model_cls.identifier] = model_cls
    return model_cls


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
