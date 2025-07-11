from dataclasses import dataclass
from datetime import datetime

from utils.base_model import BaseModel


def test_base_model_not_nested():
    @dataclass
    class TestObj(BaseModel):
        a: str
        b: int
        c: datetime

    data = {"a": "value", "b": 0, "c": "2025-07-06T03:34:55.470890"}

    test_obj = TestObj.from_dict(data)

    assert isinstance(test_obj.a, str)
    assert isinstance(test_obj.b, int)
    assert isinstance(test_obj.c, datetime)


def test_base_model_nested():
    @dataclass
    class Child(BaseModel):
        a: datetime

    @dataclass
    class Parent(BaseModel):
        children: list[Child]

    data = {
        "children": [
            {"a": "2025-07-01T03:34:55.470890"},
            {"a": "2025-07-02T03:34:55.470890"},
            {"a": "2025-07-03T03:34:55.470890"},
            {"a": "2025-07-04T03:34:55.470890"},
        ]
    }

    parent = Parent.from_dict(data)

    assert isinstance(parent.children, list)
    assert len(parent.children) == 4
    assert all(isinstance(child, Child) for child in parent.children)
    assert all(isinstance(child.a, datetime) for child in parent.children)
    assert all(child.a.day == index + 1 for index, child in enumerate(parent.children))


def test_base_model_optional():
    @dataclass
    class OptionalModel(BaseModel):
        a: str | None

    data1 = {"a": "value"}
    data2 = {"a": None}

    obj1 = OptionalModel.from_dict(data1)
    assert isinstance(obj1.a, str)

    obj2 = OptionalModel.from_dict(data2)
    assert obj2.a is None
