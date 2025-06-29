import re

__all__ = (
    "input_text_to_time_ms",
    "display_time",
    "format_time_diff",
)

_TIME_INPUT_REGEX = re.compile(r"[0-9]{6}")


def input_text_to_time_ms(text: str) -> int | None:
    """Botへ入力されたタイムを表す文字列を, ミリ秒へ変換する

    Parameters
    ----------
    text : str
        Botへ入力されたタイムを表す文字列

    Returns
    -------
    int | None
        ミリ秒へ変換されたタイム
        入力が不正な場合はNoneが返る
    """
    parsed = _TIME_INPUT_REGEX.search(text)

    if parsed is None:
        return None

    time = parsed.group(0)
    minutes, seconds, milliseconds = map(int, (time[0], time[1:3], time[3:]))

    return (minutes * 60 + seconds) * 1000 + milliseconds


def display_time(time_ms: int) -> str:
    """ミリ秒から1:23.456のような表示へ変換する．

    Parameters
    ----------
    time_ms : int
        _description_

    Returns
    -------
    str
        _description_
    """
    ms = time_ms % 1000
    time_sec = time_ms // 1000

    sec = time_sec % 60
    minutes = time_sec // 60

    return f"{minutes}:{sec:02}.{ms:03}"


def format_time_diff(diff_ms: int) -> str:
    negative = diff_ms < 0

    abs_diff = abs(diff_ms)
    ms = abs_diff % 1000

    diff_sec = abs_diff // 1000
    sec = diff_sec % 60
    minutes = diff_sec // 60

    ret = f"{sec:02}.{ms:03}"

    if minutes > 0:
        ret = f"{minutes}:{ret}"

    if negative:
        return f"-{ret}"
    return f"+{ret}"
