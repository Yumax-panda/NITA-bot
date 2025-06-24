import pytest

from utils.time import input_text_to_time_ms


@pytest.mark.parametrize(
    ("text", "expected"), [("201065", 121065), ("010123", 10123), ("12345", None)]
)
def test_input_text_to_time_ms(text: str, expected: int) -> None:
    assert input_text_to_time_ms(text) == expected
