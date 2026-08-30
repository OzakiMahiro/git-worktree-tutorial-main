# git-worktree-tutorial

`git worktree` を、ターミナル（CLI）と VS Code の GUI の両方で実際に手を動かして学ぶための練習用リポジトリです。

参考記事: [【入門】Git Worktree とは？ 初心者向けに解説](https://zenn.dev/tmasuyama1114/articles/git_worktree_beginner)

## 手順書

👉 **[docs/git-worktree-tutorial.md](docs/git-worktree-tutorial.md)**

worktree の考え方から、作成・並行作業・マージ・後片付け・つまずきポイントまでを、
**CLI コマンド**と **VS Code の GUI 操作**を各ステップで並べて説明しています。掲載しているコマンド出力はすべて実行結果です。

## Claude Code と併用する場合

👉 **[docs/claude-code-with-worktree.md](docs/claude-code-with-worktree.md)**

worktree を作ると Claude Code の会話履歴が分断されます。その理由と、どう運用すればよいかをまとめています。

## このリポジトリの中身

```
.
├── docs/
│   ├── git-worktree-tutorial.md      # 手順書（本体）
│   ├── claude-code-with-worktree.md  # Claude Code と併用するときの注意
│   └── images/                       # 手順書に差し込むスクリーンショット置き場
├── src/
│   ├── greeting.py                # greet(): 挨拶文を返す
│   └── calculator.py              # add() / multiply()
└── main.py                        # src を呼ぶだけのエントリポイント
```

`src/` は、worktree で並行編集するための題材です。中身より「複数のフォルダーで同じファイルを別々に編集できる」ことを確認するのが目的です。

## 動かし方

[uv](https://docs.astral.sh/uv/) を使います（Python 3.14）。

```bash
# サンプルの実行
uv run python main.py

# 出力
>>> こんにちは、worktreeさん！
>>> 1 + 2 = 3
>>> 3 * 4 = 12
```

> **worktree を作ったときの注意**: `.venv` は `.gitignore` 対象なので新しい worktree にはコピーされません。
> worktree 側のフォルダーで改めて `uv run python main.py`（または `uv sync`）を実行してください。

## 環境

- macOS / git 2.50.1
- VS Code 1.134.0（組み込みの Git 拡張が worktree に対応しているため、追加の拡張機能は不要）
- uv 0.11.25 / Python 3.14
