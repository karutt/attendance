import subprocess
import sys
from pathlib import Path

from simple_sheet import load_json, safe_print

# テストケースと学生リストを読み込み
test_cases = load_json("./sheets/test_case.json")
student_list = load_json("./sheets/student_list.json")

# main.py のパス
main_script = Path(__file__).parent / "main.py"

safe_print("=" * 50)
safe_print("Running tests for main.py")
safe_print("=" * 50)

for case_name, case_data in test_cases.items():
    student_id = case_data["id"]
    date = case_data["date"]
    student_name = student_list.get(student_id, "Unknown")

    safe_print(f"\n[{case_name}]")
    safe_print(f"  Student ID: {student_id}")
    safe_print(f"  Student Name: {student_name}")
    safe_print(f"  Date: {date}")
    safe_print("-" * 30)

    # main.py を実行
    result = subprocess.run(
        [sys.executable, str(main_script), student_id, date],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        safe_print(result.stdout, end="")
    if result.stderr:
        safe_print(f"  [ERROR] {result.stderr}")

safe_print("=" * 50)
safe_print("All tests completed")
safe_print("=" * 50)
