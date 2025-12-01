"""Simple Sheet ユーティリティ関数。"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

__all__ = [
    "resolve_path",
    "load_json",
]


def resolve_path(path: str | Path, stack_level: int = 1) -> Path:
    """相対パスを呼び出し元スクリプトのディレクトリを基準に解決する。

    Parameters
    ----------
    path:
        解決するパス。絶対パスの場合はそのまま返す。
    stack_level:
        呼び出し元を特定するためのスタックレベル。
        直接呼び出す場合は 1、関数内から呼び出す場合は 2 など。

    Returns
    -------
    Path
        解決された絶対パス。
    """
    resolved = Path(path)

    if not resolved.is_absolute():
        caller_frame = inspect.stack()[stack_level + 1]
        caller_file = caller_frame.filename
        caller_dir = Path(caller_file).parent
        resolved = caller_dir / resolved

    return resolved


def load_json(path: str | Path) -> Any:
    """JSONファイルを読み込んで返す。

    Parameters
    ----------
    path:
        読み込むJSONファイルのパス。
        相対パスの場合、呼び出し元スクリプトのディレクトリを基準に解決される。

    Returns
    -------
    Any
        JSONファイルの内容（dict, list など）。
    """
    json_path = resolve_path(path, stack_level=1)

    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)
