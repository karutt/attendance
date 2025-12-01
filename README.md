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

```python
from simple_sheet import open_sheet

sheet = open_sheet("gsheet")
sheet.append_row(["2025-04-01", "08:35", "1A001", "出席"])
print(sheet.get_all_rows())
```

## 開発者向け

editable mode でインストール：

```bash
pip install -e .
```
