#!/usr/bin/env python3
"""
EduAttendance セットアップスクリプト
Windows, Mac, Linux 全対応
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 50)
    print("EduAttendance セットアップ開始")
    print("=" * 50)

    # カレントディレクトリをスクリプトの場所に変更
    script_dir = Path(__file__).parent.absolute()
    print(f"\nセットアップディレクトリ: {script_dir}")

    try:
        # pip install を実行
        print("\nパッケージをインストールしています...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "."],
            cwd=script_dir
        )

        print("\n" + "=" * 50)
        print("✓ セットアップ完了！")
        print("=" * 50)
        print("\n使い方:")
        print("  python demo/sample_usage.py")
        print()

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("✗ エラーが発生しました")
        print("=" * 50)
        print(f"エラー内容: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
