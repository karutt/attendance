import subprocess
import sys
from pathlib import Path

from simple_sheet import load_json

# テストケースと学生リストを読み込み
test_cases = load_json("./sheets/test_case.json")
student_list = load_json("./sheets/student_list.json")

# main.py のパス
main_script = Path(__file__).parent / "main.py"

print("=" * 50)
print("Running tests for main.py")
print("=" * 50)

for case_name, case_data in test_cases.items():
    student_id = case_data["id"]
    date = case_data["date"]
    student_name = student_list.get(student_id, "Unknown")

    print(f"\n[{case_name}]")
    print(f"  Student ID: {student_id}")
    print(f"  Student Name: {student_name}")
    print(f"  Date: {date}")
    print("-" * 30)

    # main.py を実行（Windows環境でもUTF-8で出力を読み取る）
    result = subprocess.run(
        [sys.executable, str(main_script), student_id, date],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(f"  [ERROR] {result.stderr}")

print("=" * 50)
print("All tests completed")
print("=" * 50)
