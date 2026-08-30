"""四則演算のうち、加算と乗算だけを提供するモジュール。"""


def add(a: float, b: float) -> float:
    """
    2 つの数値を足し合わせる。

    Parameters
    ----------
    a : float
        1 つ目の数値。
    b : float
        2 つ目の数値。

    Returns
    -------
    float
        a と b の和。
    """
    return a + b


def multiply(a: float, b: float) -> float:
    """
    2 つの数値を掛け合わせる。

    Parameters
    ----------
    a : float
        1 つ目の数値。
    b : float
        2 つ目の数値。

    Returns
    -------
    float
        a と b の積。
    """
    return a * b
