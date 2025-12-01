"""Simple Sheet パッケージの公開インターフェース。

本体は ``simple_sheet.core`` にあり、ここではデフォルトシートと簡易プロキシを提供する。
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence

# .env ファイルを自動読み込み（存在すれば）
try:
    from dotenv import load_dotenv

    # 複数のパターンで .env を探す
    candidates = [
        Path.cwd() / ".env",
        Path.cwd() / "src" / ".env",
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent / "src" / ".env",
    ]

    loaded = False
    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path)
            loaded = True
            break

    # どれも見つからなければデフォルト動作
    if not loaded:
        load_dotenv()
except ImportError:
    pass  # python-dotenv がなければスキップ

from .core import (
    Cell,
    CsvSheet,
    GoogleSheet,
    InvalidParameter,
    SimpleSheet,
    open_sheet,
)
from .utils import load_json, resolve_path, safe_print

__all__ = [
    "Cell",
    "InvalidParameter",
    "SimpleSheet",
    "CsvSheet",
    "GoogleSheet",
    "open_sheet",
    "load_json",
    "resolve_path",
    "safe_print",
    "get_cell",
    "set_cell",
    "append_row",
    "get_row",
    "get_max_row",
    "clear_sheet",
]

# --- モジュールレベルの簡易プロキシ ----------------------------------------

_default_sheet = SimpleSheet()


def get_cell(row: int, col: int) -> Cell:
    """デフォルトシートからセルを取得する。"""
    return _default_sheet.get_cell(row, col)


def set_cell(row: int, col: int, value: str) -> None:
    """デフォルトシートの指定セルに値を設定する。"""
    _default_sheet.set_cell(row, col, value)


def append_row(values: Sequence[str]) -> int:
    """デフォルトシート末尾に行を追加する。"""
    return _default_sheet.append_row(values)


def get_row(row: int) -> List[Optional[str]]:
    """デフォルトシートの指定行を取得する。"""
    return _default_sheet.get_row(row)


def get_max_row() -> int:
    """デフォルトシートの最大行番号を返す。"""
    return _default_sheet.get_max_row()


def clear_sheet() -> None:
    """デフォルトシートをクリアする。"""
    _default_sheet.clear()
