"""Simple Sheet ユーティリティ関数。"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from typing import Any

__all__ = [
    "resolve_path",
    "load_json",
    "safe_print",
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


def safe_print(*args, **kwargs) -> None:
    """Windows環境でも日本語を正しく表示できるprint関数。

    通常のprint()と同じように使えるが、Windows環境では
    標準出力をUTF-8でエンコードして出力する。

    Examples
    --------
    >>> safe_print("こんにちは")
    こんにちは
    >>> safe_print("名前:", name, sep=" - ")
    名前: - 田中
    """
    # 出力文字列を構築
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    text = sep.join(str(arg) for arg in args) + end

    if sys.platform == "win32":
        # Windowsの場合、バイナリモードで直接UTF-8出力
        try:
            sys.stdout.buffer.write(text.encode("utf-8"))
            sys.stdout.flush()
        except (AttributeError, OSError):
            # バッファが使えない場合は通常のprint
            print(*args, **kwargs)
    else:
        # Unix系OSでは通常のprint
        print(*args, **kwargs)
