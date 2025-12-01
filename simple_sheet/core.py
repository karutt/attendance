"""Simple Sheet のインメモリ実装（コア）。"""

from __future__ import annotations

import csv
import io
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

from .utils import resolve_path, safe_print


if TYPE_CHECKING:
    import gspread
    from google.oauth2.service_account import Credentials

__all__ = [
    "Cell",
    "InvalidParameter",
    "SimpleSheet",
    "CsvSheet",
    "GoogleSheet",
    "open_sheet",
]


class InvalidParameter(ValueError):
    """ユーザーから渡されたパラメータが不正な場合に投げる例外。"""


@dataclass(frozen=True)
class Cell:
    """1 つのセルの情報を表すデータクラス。"""

    row: int
    col: int
    value: Optional[str]


class SimpleSheet:
    """
    メモリ上に 2 次元の表（シート）を保持するクラス。

    行番号・列番号はいずれも 1 始まりで扱い、内部的には list[list[Optional[str]]] で管理する。
    """

    def __init__(self) -> None:
        self._rows: List[List[Optional[str]]] = []

    def set_cell(self, row: int, col: int, value: str) -> None:
        """指定セルに値を設定する。必要に応じて行・列を伸ばす。"""

        self._validate_row_col(row, col)
        self._ensure_row(row)
        row_data = self._rows[row - 1]
        self._ensure_col(row_data, col)
        row_data[col - 1] = str(value)

    def get_cell(self, row: int, col: int) -> Cell:
        """指定セルの値を返す。範囲外なら value=None の Cell を返す。"""

        self._validate_row_col(row, col)
        value: Optional[str] = None
        if row <= len(self._rows):
            row_data = self._rows[row - 1]
            if col <= len(row_data):
                value = row_data[col - 1]
        return Cell(row=row, col=col, value=value)

    def append_row(self, values: Sequence[str]) -> int:
        """末尾に行を追加し、新しい行番号（1 始まり）を返す。"""

        if not values:
            raise InvalidParameter("values は 1 件以上必要です。")
        self._rows.append([str(v) for v in values])
        return len(self._rows)

    def get_row(self, row: int) -> List[Optional[str]]:
        """指定行をリストで返す。存在しない場合は空リスト。"""

        self._validate_positive(row, "row")
        if row > len(self._rows):
            return []
        return list(self._rows[row - 1])

    def get_max_row(self) -> int:
        """現在使用されている最大行番号を返す。データがなければ 0。"""

        return len(self._rows)

    def get_column(self, col: int) -> List[Optional[str]]:
        """指定列をリストで返す。存在しない場合は空リスト。"""

        self._validate_positive(col, "col")
        result = []
        for row in self._rows:
            if col <= len(row):
                result.append(row[col - 1])
            else:
                result.append(None)
        return result

    def get_max_column(self) -> int:
        """現在使用されている最大列番号を返す。データがなければ 0。"""

        if not self._rows:
            return 0
        return max(len(row) for row in self._rows)

    def get_all_rows(self) -> List[List[Optional[str]]]:
        """シート全体を 2 次元配列で返す（表示・デバッグ用）。"""

        return [list(row) for row in self._rows]

    def clear(self) -> None:
        """シートを空に戻す。"""

        self._rows.clear()

    def save_to_csv(self, path: Optional[str | Path] = None) -> Path:
        """シートの内容をCSVファイルとして保存する。

        Parameters
        ----------
        path:
            保存先のファイルパス。省略時は ./sheets/YYYYMMDD_HHMMSS.csv に保存。
            相対パスの場合、呼び出し元スクリプトのディレクトリを基準に解決される。

        Returns
        -------
        Path
            保存したファイルのパス。
        """
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = resolve_path(Path("./sheets") / f"{timestamp}.csv", stack_level=1)
        else:
            save_path = resolve_path(path, stack_level=1)

        save_path.parent.mkdir(parents=True, exist_ok=True)

        with save_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in self._rows:
                writer.writerow([cell if cell is not None else "" for cell in row])

        return save_path

    def display(self) -> None:
        """シートの内容を整形してテーブル形式で表示する。"""
        if not self._rows:
            safe_print("(empty sheet)")
            return

        # 各列の最大幅を計算
        col_widths = []
        max_cols = max(len(row) for row in self._rows) if self._rows else 0

        for col_idx in range(max_cols):
            max_width = 0
            for row in self._rows:
                if col_idx < len(row) and row[col_idx] is not None:
                    # 日本語文字を考慮した幅計算（全角=2、半角=1）
                    width = sum(2 if ord(c) > 0x7F else 1 for c in str(row[col_idx]))
                    max_width = max(max_width, width)
            col_widths.append(max_width)

        # ヘッダー区切り線
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        # 行を表示
        safe_print(separator)
        for row_idx, row in enumerate(self._rows):
            cells = []
            for col_idx in range(max_cols):
                cell_value = row[col_idx] if col_idx < len(row) and row[col_idx] is not None else ""
                # 日本語文字を考慮したパディング
                current_width = sum(2 if ord(c) > 0x7F else 1 for c in str(cell_value))
                padding = col_widths[col_idx] - current_width
                cells.append(f" {cell_value}{' ' * padding} ")

            safe_print("|" + "|".join(cells) + "|")

            # 最初の行の後に区切り線（ヘッダー扱い）
            if row_idx == 0:
                safe_print(separator)

        safe_print(separator)

    # --- 内部ユーティリティ ------------------------------------------------

    @staticmethod
    def _validate_positive(value: int, name: str) -> None:
        if not isinstance(value, int) or value < 1:
            raise InvalidParameter(f"{name} は 1 以上の整数で指定してください。")

    def _validate_row_col(self, row: int, col: int) -> None:
        self._validate_positive(row, "row")
        self._validate_positive(col, "col")

    def _ensure_row(self, row: int) -> None:
        while len(self._rows) < row:
            self._rows.append([])

    @staticmethod
    def _ensure_col(row_data: List[Optional[str]], col: int) -> None:
        while len(row_data) < col:
            row_data.append(None)


class CsvSheet(SimpleSheet):
    """CSV ファイルをストレージとして扱うシート。"""

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._load_from_csv()

    def set_cell(self, row: int, col: int, value: str) -> None:
        super().set_cell(row, col, value)
        self._flush_to_csv()

    def append_row(self, values: Sequence[str]) -> int:
        row_no = super().append_row(values)
        self._flush_to_csv()
        return row_no

    def clear(self) -> None:
        super().clear()
        self._flush_to_csv()

    def _load_from_csv(self) -> None:
        if not self._path.exists():
            return
        with self._path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            self._rows = [[cell if cell != "" else None for cell in row] for row in reader]

    def _flush_to_csv(self) -> None:
        with self._path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in self._rows:
                writer.writerow([cell if cell is not None else "" for cell in row])


class GoogleSheet(SimpleSheet):
    """Google スプレッドシートをバックエンドに使うシート。

    サービスアカウントの鍵を使って認証する。シートへの書き込みは都度 API に反映する。
    """

    def __init__(
        self,
        spreadsheet_id: str,
        worksheet: str = "1",
        credentials_path: Optional[str | Path] = None,
    ) -> None:
        super().__init__()
        try:
            import gspread
        except ImportError as exc:
            raise InvalidParameter(
                "gspread がインストールされていません。'pip install gspread google-auth' を実行してください。"
            ) from exc

        self._spreadsheet_id = spreadsheet_id
        self._worksheet_name = worksheet
        self._creds = self._build_credentials(credentials_path)
        self._client = gspread.authorize(self._creds)
        self._worksheet = self._client.open_by_key(spreadsheet_id).worksheet(worksheet)
        self._load_from_gsheet()

    def set_cell(self, row: int, col: int, value: str) -> None:
        super().set_cell(row, col, value)
        self._worksheet.update_cell(row, col, str(value))

    def append_row(self, values: Sequence[str]) -> int:
        row_no = super().append_row(values)
        self._worksheet.append_row([str(v) for v in values], value_input_option="RAW")
        return row_no

    def clear(self) -> None:
        super().clear()
        self._worksheet.clear()

    def _load_from_gsheet(self) -> None:
        # 既存値をすべて読み込み、空文字は None に揃える
        values = self._worksheet.get_all_values()
        self._rows = [[cell if cell != "" else None for cell in row] for row in values]

    @staticmethod
    def _build_credentials(credentials_path: Optional[str | Path]):
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        # 環境変数から認証情報を構築（JSONファイル不要）
        if os.environ.get("GOOGLE_PRIVATE_KEY"):
            credentials_info = {
                "type": os.environ.get("GOOGLE_TYPE", "service_account"),
                "project_id": os.environ.get("GOOGLE_PROJECT_ID", ""),
                "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID", ""),
                "private_key": os.environ.get("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
                "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL", ""),
                "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
                "auth_uri": os.environ.get(
                    "GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": os.environ.get(
                    "GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"
                ),
                "auth_provider_x509_cert_url": os.environ.get(
                    "GOOGLE_AUTH_PROVIDER_X509_CERT_URL",
                    "https://www.googleapis.com/oauth2/v1/certs",
                ),
                "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL", ""),
                "universe_domain": os.environ.get("GOOGLE_UNIVERSE_DOMAIN", "googleapis.com"),
            }
            return Credentials.from_service_account_info(credentials_info, scopes=scopes)

        # フォールバック: JSONファイルから読み込み
        path = (
            Path(credentials_path).expanduser()
            if credentials_path is not None
            else Path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")).expanduser()
        )
        if not path.exists():
            raise InvalidParameter(
                "認証情報が見つかりません。環境変数 GOOGLE_PRIVATE_KEY か "
                "GOOGLE_APPLICATION_CREDENTIALS を確認してください。"
            )
        return Credentials.from_service_account_file(path, scopes=scopes)


def open_sheet(
    online: bool = False,
    path: Optional[str | Path] = None,
    spreadsheet_id: Optional[str] = None,
    worksheet: str = "1",
    credentials_path: Optional[str | Path] = None,
) -> SimpleSheet:
    """シートを開く（なければ作成）。

    Parameters
    ----------
    online:
        True なら Google Sheets、False なら CSV。デフォルトは False（オフライン）。
    path:
        CSV の場合のファイルパス。省略時は自動検出。
    spreadsheet_id:
        Google Sheets の場合のスプレッドシート ID（省略時は GOOGLE_SPREADSHEET_ID 環境変数）。
    worksheet:
        Google Sheets のワークシート名。デフォルト "1"（環境変数 GOOGLE_WORKSHEET_NAME でも指定可）。
    credentials_path:
        Google Sheets のサービスアカウント鍵パス（省略時は GOOGLE_APPLICATION_CREDENTIALS 環境変数）。
    """

    if not online:
        # オフライン: CSV
        if path is None:
            # デフォルト: attendance.csv を複数のパターンで探す
            csv_path = resolve_path("./sheets/attendance.csv", stack_level=1)
        else:
            # path が指定された場合、呼び出し元スクリプトのディレクトリを基準に解決
            csv_path = resolve_path(path, stack_level=1)

        return CsvSheet(csv_path)
    else:
        # オンライン: Google Sheets
        spreadsheet_id = spreadsheet_id or os.environ.get("GOOGLE_SPREADSHEET_ID")
        if spreadsheet_id is None:
            raise InvalidParameter(
                "online=True には spreadsheet_id が必要です。引数か環境変数 GOOGLE_SPREADSHEET_ID を指定してください。"
            )
        worksheet_name = worksheet or os.environ.get("GOOGLE_WORKSHEET_NAME", "Sheet1")
        credentials = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        return GoogleSheet(
            spreadsheet_id=spreadsheet_id,
            worksheet=worksheet_name,
            credentials_path=credentials,
        )
