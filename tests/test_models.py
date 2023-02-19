import sdif.fields as fields
import sdif.model_meta as model_meta


def test_m1_m2_exclusive():
    for cls in model_meta.REGISTERED_MODELS.values():
        for field in fields.record_fields(cls):
            assert not (field.m1 and field.m2)
