import sdif.fields as fields
import sdif.models as models
import sdif.model_meta as model_meta


def test_m1_m2_exclusive():
    for cls in model_meta.REGISTERED_MODELS.values():
        for field in fields.record_fields(cls):
            assert not (field.m1 and field.m2)


def test_optional_m1_metadata():
    (field,) = [f for f in fields.record_fields(models.RelayName) if f.name == "prelim_order"]
    assert field.m1 == True
    assert field.optional == True
