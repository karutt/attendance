# EduAttendance

出席管理システム用のシンプルなスプレッドシート抽象化ライブラリ。

## セットアップ方法

### Windows

1. `setup.bat` をダブルクリック
2. 完了を待つ

### Mac / Linux

1. ターミナルを開く
2. 以下を実行：

```bash
./setup.sh
```

または直接：

```bash
python3 setup.py
```

## 使用例

### 基本的な使い方

```python
from simple_sheet import open_sheet

# CSVファイルを開く（デフォルト：./sheets/attendance.csv）
sheet = open_sheet(path="./sheets/attendance.csv")

# データを表示
sheet.display()

# セルに値を設定
sheet.set_cell(row=2, col=3, value="○")

# 行を追加
sheet.append_row(["田中太郎", "○", "○", "○"])
```

### 日本語表示（Windows環境）

このプロジェクトはWindows環境での日本語文字化けに完全対応しています。

```python
from simple_sheet import safe_print

# Windows環境でも正しく日本語を表示
safe_print("こんにちは、世界")
safe_print("名前:", name, "年齢:", age)

# シートの表示も自動的に文字化け対策済み
sheet.display()  # テーブル形式で日本語が正しく表示されます
```

**重要な注意点：**
- すべてのファイルはUTF-8エンコーディングで保存されています
- `safe_print()`を使うと、Windows/Mac/Linux問わず日本語が正しく表示されます
- VSCodeやWindows Terminalなど、UTF-8対応のターミナルでの使用を推奨します

## 開発者向け

editable mode でインストール：

```bash
pip install -e .
```
