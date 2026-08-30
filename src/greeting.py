"""挨拶文を組み立てるモジュール。"""


def greet(name: str) -> str:
    """
    名前を受け取って挨拶文を返す。

    Parameters
    ----------
    name : str
        挨拶する相手の名前。

    Returns
    -------
    str
        組み立てた挨拶文。
    """
    return f"こんにちは、{name}さん！"


def greet_en(name: str) -> str:
    """
    名前を受け取って英語の挨拶文を返す。

    Parameters
    ----------
    name : str
        挨拶する相手の名前。

    Returns
    -------
    str
        組み立てた英語の挨拶文。
    """
    return f"Hello, {name}!"
