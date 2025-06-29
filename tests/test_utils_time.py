import pytest

from utils.time import display_time, format_time_diff, input_text_to_time_ms


@pytest.mark.parametrize(
    ("text", "expected"), [("201065", 121065), ("010123", 10123), ("12345", None)]
)
def test_input_text_to_time_ms(text: str, expected: int) -> None:
    assert input_text_to_time_ms(text) == expected


@pytest.mark.parametrize(
    ("time_ms", "expected"), [(121065, "2:01.065"), (10123, "0:10.123")]
)
def test_display_time(time_ms: int, expected: str) -> None:
    assert display_time(time_ms) == expected


@pytest.mark.parametrize(
    ("diff_ms", "expected"),
    [
        (-1234, "-1.234"),
        (1234, "+1.234"),
        (234, "+0.234"),
        (-234, "-0.234"),
        (72340, "+1:12.340"),
        (-72340, "-1:12.340"),
    ],
)
def test_format_time_diff(diff_ms: int, expected: str) -> None:
    assert format_time_diff(diff_ms) == expected
