from teacher_dashboard import TeacherDashboard

if __name__ == "__main__":
    # For testing purposes, hardcode teacher_id (replace with actual login logic later)
    teacher_id = "T001"
    app = TeacherDashboard(teacher_id)
    app.mainloop()