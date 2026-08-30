# git worktree と Claude Code を併用するときの注意

`git worktree` で作業フォルダーを分けると、**Claude Code の会話履歴も worktree ごとに分断されます**。
このドキュメントは、その理由（実際に手元で確認した内容）と、取りうる対処法を整理したものです。

- 対象: [git worktree ハンズオン手順書](git-worktree-tutorial.md) の内容を Claude Code と組み合わせて使う人
- 検証環境: macOS / git 2.50.1 / VS Code 1.134.0 / Claude Code（VS Code 拡張）
- パスのうち各自の環境で異なる部分は `<<PATH_TO_PROJECT>>` / `~/...` と省略表記にしています

> **先に結論**
> 1. 履歴は **cwd（起動したフォルダー）ごと**に保存されるので、worktree を作ると必ず別扱いになる
> 2. **worktree の置き場所を変えても解決しません**（VS Code の既定値でも、リポジトリ内の `.worktree/` でも同じ）
> 3. 実運用は「**履歴そのものを共有しようとせず、引き継ぎ情報をリポジトリ側のファイルで共有する**」のが素直

---

## 目次

- [git worktree と Claude Code を併用するときの注意](#git-worktree-と-claude-code-を併用するときの注意)
  - [目次](#目次)
  - [1. 会話履歴はどこに保存されているか](#1-会話履歴はどこに保存されているか)
  - [2. なぜ worktree で履歴が分断されるのか](#2-なぜ-worktree-で履歴が分断されるのか)
  - [3. 置き場所を変えても解決しない](#3-置き場所を変えても解決しない)
  - [4. 対処法の比較](#4-対処法の比較)
    - [A. 引き継ぎ情報をリポジトリ側で共有する（推奨）](#a-引き継ぎ情報をリポジトリ側で共有する推奨)
    - [B. `memory/` をリンクで共有する（Windows で動作確認済み）](#b-memory-をリンクで共有するwindows-で動作確認済み)
    - [C. 親フォルダーから 1 つのセッションを動かす](#c-親フォルダーから-1-つのセッションを動かす)
  - [5. 推奨する運用](#5-推奨する運用)
  - [6. まとめ](#6-まとめ)

---

## 1. 会話履歴はどこに保存されているか

Claude Code のセッション履歴は、ホーム配下の `~/.claude/projects/` に**プロジェクト単位のフォルダー**として保存されています。

```bash
ls -1 ~/.claude/projects/

# 出力（抜粋）
>>> -Users-ozakimahiro-my-workspace---------class-di-test
>>> -Users-ozakimahiro-my-workspace---------databricks-dab
>>> -Users-ozakimahiro-my-workspace---------git-worktree-tutorial-git-worktree-tutorial-main
```

このフォルダー名は、**Claude Code を起動したときの cwd（カレントディレクトリ）の絶対パスを変換したもの**です。変換規則はシンプルで、**英数字以外の 1 文字が (ハイフン)`-` 1 個になる**だけです。

| 元のパス | 変換後 |
|---|---|
| `/` | `-` |
| `_`（`my_workspace`） | `-`（`my-workspace`） |
| 日本語 1 文字（`日`, `本`, …） | `-` 1 個 |

このリポジトリの例で確かめると、次のように一致します。

```
/Users/ozakimahiro/my_workspace/日本語フォルダ/git-worktree-tutorial/git-worktree-tutorial-main
                               ↑            ↑
                               / + 7文字 + / = 「-」9個

-Users-ozakimahiro-my-workspace---------git-worktree-tutorial-git-worktree-tutorial-main
```

中身はこうなっています。

```bash
ls -la ~/.claude/projects/-Users-ozakimahiro-...-git-worktree-tutorial-main/

# 出力
>>> -rw-------  a7456008-8f4d-4d5e-ab1e-4911b99b869f.jsonl   ← セッション1の会話ログ
>>> -rw-------  c2b8d01c-7b47-46ad-a30f-f470db826b2f.jsonl   ← セッション2の会話ログ
>>> drwxr-xr-x  memory/                                      ← このプロジェクトの記憶
```

- `*.jsonl` … 1 セッション = 1 ファイル。`/resume` や `--continue` はここから候補を探します
- `memory/` … プロジェクトに紐づく記憶ファイル置き場

---

## 2. なぜ worktree で履歴が分断されるのか

1 章のとおり、**保存先フォルダーは cwd のパスから機械的に決まります**。
worktree は「同じリポジトリを別のパスに展開する」機能なので、当然 cwd が変わります。

```
本体     /...(略).../git-worktree-tutorial-main
            → ~/.claude/projects/-Users-...-git-worktree-tutorial-main/

worktree /...(略).../git-worktree-tutorial-main.worktrees/feature-new-ui
            → ~/.claude/projects/-Users-...-git-worktree-tutorial-main-worktrees-feature-new-ui/
```

保存先が別フォルダーになるため、worktree 側の Claude Code からは次のものが**一切見えません**。

- 本体側のセッション履歴（`/resume`・`--continue` の候補に出ない）
- 本体側の `memory/`

なお、これは Claude Code の不具合ではなく「作業フォルダーごとに文脈を分ける」という設計です。**タスクごとに文脈が混ざらない**という利点でもあります。

---

## 3. 置き場所を変えても解決しない

「worktree をリポジトリの中（例: `.worktree/`）に置けば同じプロジェクト扱いになるのでは？」と考えたくなりますが、**なりません**。判定は cwd の**パス文字列**だけで、リポジトリの所属を見ているわけではないからです。

| 置き方 | パス | 履歴の共有 | 補足 |
|---|---|---|---|
| VS Code の既定値 | `<親>/git-worktree-tutorial-main.worktrees/feature-new-ui` | ❌ されない | リポジトリの**外**なので `.gitignore` 不要 |
| 記事流の横並び | `<親>/git-worktree-tutorial-new-ui` | ❌ されない | 親フォルダーに兄弟が増えていく |
| リポジトリ内 | `<repo>/.worktree/feature-new-ui` | ❌ されない | **`.gitignore` 必須**（下記） |

> **リポジトリ内に置く場合の注意**: worktree のファイルが本体の作業ツリーの中に現れるため、`.gitignore` に追加しないと `git status` に出てきます。また Claude Code のファイル検索（Grep / Glob）や `ripgrep` が worktree 側も走査してしまい、**同じファイルが二重にヒットして混乱の原因になります**。

履歴の共有という観点ではどれも同じなので、**VS Code の既定値（`<repo 名>.worktrees/` 配下）をそのまま使うのが無難**です。リポジトリの外に出つつ 1 フォルダーにまとまるため、`.gitignore` の設定も散らかりも発生しません。

---

## 4. 対処法の比較

| | 共有できるもの | worktree の並列作業 | 手軽さ | 総評 |
|---|---|---|---|---|
| A. 引き継ぎ情報をファイル共有 | 前提知識・決定事項 | ✅ 活かせる | ◎ | **推奨** |
| B. `memory/` をリンクで共有 | プロジェクトの記憶 | ○ 保てる | △ | Windows で動作確認済み |
| C. 親フォルダーから 1 セッション | 履歴・記憶のすべて | ❌ 失われる | ○ | 使いどころは限定的 |

### A. 引き継ぎ情報をリポジトリ側で共有する（推奨）

そもそも共有したいのは**会話ログそのものではなく、前提知識と決定事項**のはずです。それはリポジトリ内のファイルに置けば、**worktree を作った時点で自動的にコピーされます**（git 管理下のファイルなので）。

| 置き場所 | 共有されるか | 用途 |
|---|---|---|
| `CLAUDE.md`（コミット） | ✅ される | プロジェクト規約、アーキテクチャ、実行コマンド |
| `.claude/settings.json`（コミット） | ✅ される | 権限設定・フックを全 worktree で統一 |
| `docs/*.md`（コミット） | ✅ される | 設計判断、作業メモ、引き継ぎノート |
| `.claude/settings.local.json` | ❌ されない | 個人設定（`.gitignore` 対象のため） |
| `.venv` | ❌ されない | `.gitignore` 対象。worktree 側で `uv sync` が必要 |

運用のコツは、**worktree を切る前に文脈を書き出しておく**ことです。

> 「ここまでの決定事項と残タスクを `docs/handoff-feature-new-ui.md` にまとめて」

と依頼してからブランチを切れば、新しい worktree の Claude はそのファイルを読んで続きから作業できます。

### B. `memory/` をリンクで共有する（Windows で動作確認済み）

1 章のとおり、プロジェクトの記憶は `~/.claude/projects/<変換後の名前>/memory/` に置かれているだけです。
そこで、**worktree 側の `memory/` を本体側の `memory/` へリンクしてしまえば、記憶を 1 か所に集約できます**。

ポイントは、**会話ログ（`*.jsonl`）はリンクせず、`memory/` だけを共有する**ことです。プロジェクトフォルダーごとリンクすると `/resume` の候補も共有できますが、複数 worktree で同時にセッションを走らせたときに**セッションファイルの書き込みが競合する恐れ**があります。`memory/` だけなら並列作業を保ったまま記憶を共有できます。

**Windows（ジャンクション）**

```bat
mklink /J "%USERPROFILE%\.claude\projects\<worktree のフォルダー名>\memory" ^
          "%USERPROFILE%\.claude\projects\<本体のフォルダー名>\memory"
```

**macOS / Linux（シンボリックリンク）**

```bash
ln -s ~/.claude/projects/<本体のフォルダー名>/memory \
      ~/.claude/projects/<worktree のフォルダー名>/memory
```

検証状況:

| 環境 | 方式 | 結果 |
|---|---|---|
| Windows | ジャンクション（`mklink /J`） | ✅ 動作を確認済み |
| macOS（この環境） | シンボリックリンク（`ln -s`） | ⚠️ 未検証 |

> **ジャンクションを自動で張るスクリプト**: **TBC**（後日ここに追記します）

注意点:

- 公式にサポートされた使い方ではないため、Claude Code の更新で挙動が変わる可能性があります
- リンク先（本体側）の `memory/` を消すと、リンク元がすべて壊れます
- worktree を削除しても `~/.claude/projects/` 側のフォルダーは残るので、**リンクも手で掃除する**必要があります
- worktree のパスが決まってからでないと張れません（フォルダー名が cwd から決まるため）

### C. 親フォルダーから 1 つのセッションを動かす

worktree 群をまとめている**親フォルダー**で Claude Code を起動します。cwd が固定されるので、履歴も `memory/` も 1 本になります。

```
git-worktree-tutorial/                     ← ここで起動する
├── git-worktree-tutorial-main/
└── git-worktree-tutorial-main.worktrees/
    └── feature-new-ui/
```

Claude はどの worktree のファイルも読み書きできます。ただし代償があります。

- **worktree 最大の利点である「複数セッションの並列作業」が失われる**
- **cwd が git リポジトリの外になる**ため、git の自動コンテキスト（起動時のブランチ・変更ファイル表示）や、リポジトリを前提とする機能（`/code-review` など）が効かなくなる
- git 操作のたびに `git -C git-worktree-tutorial-main status` のようにパス指定が必要

「複数 worktree を横断して一気に直したい」ときの一時的な手段、と考えるのが妥当です。

---

## 5. 推奨する運用

1. **worktree の置き場所は VS Code の既定値のまま**（`<repo 名>.worktrees/` 配下）にする
2. **worktree ごとに Claude Code を立てる**。履歴が分かれることは受け入れる（タスクごとに文脈がきれいになる、という利点として使う）
3. **共有したい知識は `CLAUDE.md` / `docs/` に書いてコミットする**
4. worktree を切る前に、**引き継ぎノートを書き出させる**
5. 新しい worktree では、まず `uv sync`（または `uv run python main.py`）で `.venv` を用意する
6. 記憶まで引き継ぎたければ、**`memory/` をリンクで共有する**（4-B。Windows ではジャンクションで動作確認済み）
7. 複数 worktree を横断する作業が必要なときだけ、**一時的に親フォルダーから 1 セッション**を動かす

---

## 6. まとめ

- Claude Code の履歴は `~/.claude/projects/<cwd のパスを変換した名前>/` に保存される
- worktree は cwd が変わるので、**履歴・`memory/` は必ず分断される**
- **置き場所（既定値 / 横並び / リポジトリ内）を変えても、この点は一切変わらない**
- 履歴を無理に共有するより、**`CLAUDE.md` と `docs/` で引き継ぐ**ほうが、worktree の並列性を活かせて安全

| 知りたいこと | 答え |
|---|---|
| worktree 間で `/resume` できる？ | ❌ できない |
| `.worktrees/` 配下にすれば解決する？ | ❌ しない（パスが違えば別プロジェクト） |
| 実質どうすればいい？ | `CLAUDE.md` / `docs/` で引き継ぐ |
| 記憶（`memory/`）だけでも共有したい | リンクで共有できる（Windows のジャンクションで確認済み） |
| どうしても 1 本にしたい | 親フォルダーから 1 セッション（並列作業は諦める） |
