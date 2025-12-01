import sys
from simple_sheet import open_sheet, load_json

# ---- test code ----
# student_id = sys.argv[1] if len(sys.argv) > 1 else None
# now = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M:%S") if len(sys.argv) > 2 else None


sheet = open_sheet(path="./sheets/attendance.csv")
student_list = load_json("./sheets/student_list.json")
print(student_list)

sheet.set_cell(1, 1, "12月")
sheet.display()
