students_db = [
    {"id": 1, "name": "Nguyễn Văn A"},
    {"id": 2, "name": "Trần Thị B"}
]

def get_students():
    return students_db

def get_student_by_id(id):
    for student in students_db:
        if student["id"] == id:
            return student
    return {"message": "Không tìm thấy học sinh"}, 404