"""git worktree ハンズオン用のエントリポイント。"""

from src.calculator import add, multiply
from src.greeting import greet


def main() -> None:
    """
    サンプル関数を呼び出して結果を標準出力に表示する。

    Returns
    -------
    None
        戻り値はない。
    """
    print(greet("worktree"))
    print(f"1 + 2 = {add(1, 2)}")
    print(f"3 * 4 = {multiply(3, 4)}")


if __name__ == "__main__":
    main()
