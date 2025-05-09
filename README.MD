# Attendance Management System

A Python-based attendance management system using Tkinter for the GUI and Oracle SQL for the database.

## Features

- Login for students and teachers
- Student dashboard
- Teacher dashboard
- Attendance recording
- Leave requests

## Technologies Used

- Python
- Tkinter
- Oracle SQL

## Setup

1.  Install Python and Oracle SQL Developer.
2.  Set up the Oracle database.
3.  Clone this repository.
4.  Run the application.

## Database Schema

- CREATE TABLE teachers (
  teacher_id VARCHAR2(50) PRIMARY KEY,
  first_name VARCHAR2(50) NOT NULL,
  last_name VARCHAR2(50) ,
  date_of_birth DATE,
  gender VARCHAR2(10) ,
  age NUMBER,
  contact_no VARCHAR2(15) ,
  address VARCHAR2(200),
  department_name VARCHAR2(100) NOT NULL,
  email VARCHAR2(100) UNIQUE NOT NULL,
  password VARCHAR2(100) NOT NULL,
  salary NUMBER(20,3)
  );
  ALTER TABLE teachers
  MODIFY date_of_birth DATE;
  ALTER TABLE teachers
  MODIFY last_name varchar(50);

CREATE TABLE courses (
course_id VARCHAR2(50) PRIMARY KEY,
course_name VARCHAR2(100) UNIQUE NOT NULL
);

CREATE TABLE assignments (
assignment_id NUMBER PRIMARY KEY,
teacher_id varchar(50),
course_id varchar(50) ,
FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
CREATE TABLE students (
student_id VARCHAR2(50) PRIMARY KEY,
first_name VARCHAR2(50) NOT NULL,
last_name VARCHAR2(50),
date_of_birth DATE,
gender VARCHAR2(10),
age NUMBER,
contact_no VARCHAR2(15),
address VARCHAR2(200),
department_name VARCHAR2(100) NOT NULL,
email VARCHAR2(100) NOT NULL,
password VARCHAR2(100) NOT NULL
);

CREATE TABLE enrollments (
enrollment_id NUMBER PRIMARY KEY,
student_id varchar(50) ,
course_id varchar(50) ,
FOREIGN KEY (student_id) REFERENCES students(student_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
CREATE TABLE attendance (
attendance_id NUMBER PRIMARY KEY,
student_id varchar(50) ,
course_id varchar(50) ,
date_attended DATE NOT NULL,
status VARCHAR2(10) CHECK (status IN ('Present', 'Absent')),
FOREIGN KEY (student_id) REFERENCES students(student_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
ALTER TABLE attendance
MODIFY status VARCHAR2(10) DEFAULT 'Absent' CHECK (status IN ('Present', 'Absent'));
--add the column first then will be able to set it to default

ALTER TABLE attendance
ADD day_attended VARCHAR2(15);
UPDATE attendance
SET day_attended = TRIM(TO_CHAR(date_attended, 'Day'));

SELECT _ FROM STUDENTS;
SELECT _ FROM attendance;
SELECT _ FROM TEACHERS;
SELECT _ FROM courses;
SELECT _ FROM assignments;
SELECT _ FROM enrollments;

INSERT INTO teachers (teacher_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password, salary)
VALUES ('T001', 'Ali', 'Khan', DATE '2002-05-20', 'Male', 48, '03001234567', 'House #12, Lahore', 'Software Engineering', 'ali.khan@university.edu.pk', 'secure123', 120000.500);

INSERT INTO teachers (teacher_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password, salary)
VALUES ('T002', 'Fatima', 'Ahmed', DATE '2001-08-15', 'Female', 43, '03129876543', 'House #34, Islamabad', 'Mathematics', 'fatima.ahmed@university.edu.pk', 'mypassword', 95000.300);

INSERT INTO teachers (teacher_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password, salary)
VALUES ('T003', 'Zain', 'Hussain', DATE '2000-03-10', 'Male', 36, '03214567890', 'House #56, Karachi', 'Computer Science', 'zain.hussain@university.edu.pk', 'password123', 105000.750);

UPDATE teachers
SET date_of_birth = DATE '1985-12-25' -- Replace with the desired date
WHERE teacher_id = 'T001'; -- Replace with the specific teacher's ID

UPDATE teachers
SET date_of_birth = DATE '1990-12-25' -- Replace with the desired date
WHERE teacher_id = 'T002'; -- Replace with the specific teacher's ID

UPDATE teachers
SET date_of_birth = DATE '1979-12-25' -- Replace with the desired date
WHERE teacher_id = 'T003'; -- Replace with the specific teacher's ID

------courses table

INSERT INTO courses (course_id, course_name)
VALUES ('CS101', 'Introduction to Computer Science');

INSERT INTO courses (course_id, course_name)
VALUES ('SE202', 'Software Engineering Fundamentals');

INSERT INTO courses (course_id, course_name)
VALUES ('MATH301', 'Advanced Mathematics');

INSERT INTO courses (course_id, course_name)
VALUES ('IT404', 'Information Technology Basics');

-------assignment table
INSERT INTO assignments (assignment_id, teacher_id, course_id)
VALUES (1, 'T001', 'SE202');

INSERT INTO assignments (assignment_id, teacher_id, course_id)
VALUES (2, 'T002', 'MATH301');

INSERT INTO assignments (assignment_id, teacher_id, course_id)
VALUES (3, 'T003', 'CS101');

--------students

INSERT INTO students (student_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password)
VALUES ('21-SE-01', 'Ayesha', 'Bano', DATE '2003-01-05', 'Female', 22, '03331234567', 'House #67, Multan', 'Software Engineering', 'ayesha.bano@university.edu.pk', 'ayesha123');

INSERT INTO students (student_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password)
VALUES ('21-SE-13', 'Ahmad', 'Kamal', DATE '2003-07-18', 'Male', 22, '03456789012', 'House #89, Lahore', 'Software Engineering', 'ahmad.kamal@university.edu.pk', 'ahmad456');

INSERT INTO students (student_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password)
VALUES ('22-CS-07', 'Sara', 'Zafar', DATE '2004-03-12', 'Female', 21, '03012345678', 'House #45, Karachi', 'Computer Science', 'sara.zafar@university.edu.pk', 'sara789');

INSERT INTO students (student_id, first_name, last_name, date_of_birth, gender, age, contact_no, address, department_name, email, password)
VALUES ('22-CS-19', 'Bilal', 'Hassan', DATE '2004-09-25', 'Male', 21, '03219876543', 'House #78, Peshawar', 'Computer Science', 'bilal.hassan@university.edu.pk', 'bilal987');

----enrollments

INSERT INTO enrollments (enrollment_id, student_id, course_id)
VALUES (1, '21-SE-01', 'SE202');

INSERT INTO enrollments (enrollment_id, student_id, course_id)
VALUES (2, '21-SE-13', 'SE202');

INSERT INTO enrollments (enrollment_id, student_id, course_id)
VALUES (3, '22-CS-07', 'CS101');

INSERT INTO enrollments (enrollment_id, student_id, course_id)
VALUES (4, '22-CS-19', 'CS101');

----attendance
INSERT INTO attendance (attendance_id, student_id, course_id, date_attended, status)
VALUES (1, '21-SE-01', 'SE202', DATE '2025-04-18', 'Present');

INSERT INTO attendance (attendance_id, student_id, course_id, date_attended, status)
VALUES (2, '21-SE-13', 'SE202', DATE '2025-04-18', 'Absent');

INSERT INTO attendance (attendance_id, student_id, course_id, date_attended, status)
VALUES (3, '22-CS-07', 'CS101', DATE '2025-04-18', 'Present');

INSERT INTO attendance (attendance_id, student_id, course_id, date_attended, status)
VALUES (4, '22-CS-19', 'CS101', DATE '2025-04-18', 'Present');

SELECT name FROM v$database;
SELECT teacher_id
FROM teachers
WHERE LOWER(email) = LOWER('ali.khan@university.edu.pk') AND password = 'secure123';
SELECT teacher_id
FROM teachers
WHERE email = 'ali.khan@university.edu.pk' AND password = 'secure123';

SELECT _ FROM STUDENTS;
SELECT _ FROM attendance;
SELECT _ FROM TEACHERS;
SELECT _ FROM courses;
SELECT _ FROM assignments;
SELECT _ FROM enrollments;

ALTER TABLE assignments ADD (weeks NUMBER, total_classes NUMBER);
ALTER TABLE attendance ADD (class_number NUMBER);
ALTER TABLE attendance MODIFY status VARCHAR2(10);

SELECT student_id, first_name, last_name, email, password FROM students FETCH FIRST 5 ROWS ONLY;

CREATE TABLE leave_requests (
request_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
student_id VARCHAR2(50) NOT NULL,
course_id VARCHAR2(50) NOT NULL,
leave_date DATE NOT NULL,
reason VARCHAR2(255) NOT NULL,
status VARCHAR2(20) DEFAULT 'Pending',
FOREIGN KEY (student_id) REFERENCES students(student_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id)

);

CREATE SEQUENCE attendance_seq
START WITH 1
INCREMENT BY 1
NOCACHE

SELECT column_name
FROM user_cons_columns
WHERE constraint_name = 'SYS_C007885';

SELECT constraint_name, search_condition
FROM user_constraints
WHERE table_name = 'ATTENDANCE' AND constraint_type = 'C';

ALTER TABLE attendance MODIFY status CHECK (status IN ('Present', 'Absent', 'Leave'));

SELECT DISTINCT status FROM attendance;

SELECT student_id, date_attended, status FROM attendance WHERE course_id = 'SE202' ORDER BY date_attended DESC;

SELECT table_name
FROM all_tables
WHERE table_name = 'LEAVE_REQUESTS';
SELECT \* FROM "LEAVE_REQUESTS"; -- If the table was created in lowercase

SELECT column_name FROM all_tab_columns WHERE table_name = 'ATTENDANCE';

SELECT \* FROM ATTENDANCE WHERE COURSE_ID = :course_id ORDER BY DATE_ATTENDED DESC;

SELECT constraint_name, search_condition
FROM user_constraints
WHERE table_name = 'ATTENDANCE' AND constraint_type = 'C';

ALTER TABLE attendance DROP CONSTRAINT SYS_C007881;
ALTER TABLE attendance DROP CONSTRAINT SYS_C007885;

CREATE OR REPLACE VIEW student_courses_view AS
SELECT s.student_id, c.course_id, c.course_name
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id;

CREATE OR REPLACE VIEW course_attendance_view AS
SELECT student_id, course_id, date_attended, day_attended, status
FROM attendance;

CREATE OR REPLACE VIEW student_attendance_course_view AS
SELECT student_id, course_id, date_attended, day_attended, status
FROM attendance;

CREATE OR REPLACE VIEW pending_leave_requests_view AS
SELECT
lr.student_id,
c.course_id,
c.course_name,
lr.leave_date,
lr.reason,
lr.status
FROM leave_requests lr
JOIN courses c ON lr.course_id = c.course_id
WHERE lr.status = 'Pending';

-- View to get courses for a specific student
CREATE OR REPLACE VIEW student_courses_view AS
SELECT c.course_id, c.course_name, e.student_id
FROM courses c
JOIN enrollments e ON c.course_id = e.course_id;

-- View to get attendance records for a specific student in a specific course
CREATE OR REPLACE VIEW student_attendance_course_view AS
SELECT
a.student_id,
a.course_id,
TO_CHAR(a.date_attended, 'YYYY-MM-DD') AS date_attended,
a.day_attended,
a.status
FROM attendance a;

-- View to get courses assigned to a specific teacher
CREATE OR REPLACE VIEW teacher_courses_view AS
SELECT c.course_id, c.course_name, a.teacher_id
FROM courses c
JOIN assignments a ON c.course_id = a.course_id;

-- View to get students enrolled in a specific course
CREATE OR REPLACE VIEW course_students_view AS
SELECT s.student_id, s.first_name, s.last_name, e.course_id
FROM students s
JOIN enrollments e ON s.student_id = e.student_id;

-- View to get pending leave requests with course names (assuming you want all pending)
CREATE OR REPLACE VIEW pending_leave_requests_view AS
SELECT
lr.student_id,
c.course_name,
TO_CHAR(lr.leave_date, 'YYYY-MM-DD') AS leave_date,
lr.reason,
lr.status
FROM leave_requests lr
JOIN courses c ON lr.course_id = c.course_id
WHERE lr.status = 'Pending';

SELECT column_name
FROM user_tab_cols
WHERE table_name = 'COURSES';

SELECT text FROM user_views WHERE view_name = 'PENDING_LEAVE_REQUESTS_VIEW';

SELECT column_name
FROM user_tab_cols
WHERE table_name = 'COURSES';

SELECT column_name
FROM user_tab_cols
WHERE table_name = 'COURSES';

DROP VIEW pending_leave_requests_view;

CREATE OR REPLACE VIEW pending_leave_requests_view AS
SELECT
lr.student_id,
c."COURSE_NAME",
TO_CHAR(lr.leave_date, 'YYYY-MM-DD') AS leave_date,
lr.reason,
lr.status
FROM leave_requests lr
JOIN courses c ON lr.course_id = c.course_id
WHERE lr.status = 'Pending';

DROP VIEW pending_leave_requests_view;

CREATE OR REPLACE VIEW pending_leave_requests_view AS
SELECT
lr.student_id,
c.COURSE_NAME,
TO_CHAR(lr.leave_date, 'YYYY-MM-DD') AS leave_date,
lr.reason,
lr.status
FROM leave_requests lr
JOIN courses c ON lr.course_id = c.course_id
WHERE lr.status = 'Pending';

DROP VIEW pending_leave_requests_view;

CREATE OR REPLACE VIEW pending_leave_requests_view AS
SELECT
lr.student_id AS student_id,
c.course_name AS course_name,
TO_CHAR(lr.leave_date, 'YYYY-MM-DD') AS leave_date,
lr.reason AS reason,
lr.status AS status
FROM leave_requests lr
JOIN courses c ON lr.course_id = c.course_id
WHERE lr.status = 'Pending';

DROP VIEW pending_leave_requests_view;

CREATE OR REPLACE VIEW pending_leave_requests_view AS
SELECT
lr.STUDENT_ID AS student_id,
c.COURSE_NAME AS course_name,
TO_CHAR(lr.LEAVE_DATE, 'YYYY-MM-DD') AS leave_date,
lr.REASON AS reason,
lr.STATUS AS status
FROM leave_requests lr
JOIN courses c ON lr.COURSE_ID = c.COURSE_ID
WHERE lr.STATUS = 'Pending';

DESCRIBE leave_requests;
DESCRIBE courses;

CREATE VIEW student_attendance_view AS
SELECT
a.DATE_ATTENDED,
a.STATUS,
a.STUDENT_ID,
a.COURSE_ID
FROM ATTENDANCE a;

CREATE OR REPLACE PROCEDURE GET_ATTENDANCE_STATS (
p_student_id IN VARCHAR2,
p_course_id IN VARCHAR2,
p_present_count OUT NUMBER,
p_absent_count OUT NUMBER,
p_leave_count OUT NUMBER,
p_total_count OUT NUMBER
)
AS
BEGIN
SELECT
SUM(CASE WHEN status = 'Present' OR status = 'Leave' THEN 1 ELSE 0 END),
SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END),
SUM(CASE WHEN status = 'Leave' THEN 1 ELSE 0 END),
COUNT(\*)
INTO
p_present_count,
p_absent_count,
p_leave_count,
p_total_count
FROM attendance
WHERE student_id = p_student_id
AND course_id = p_course_id;
END GET_ATTENDANCE_STATS;
/
