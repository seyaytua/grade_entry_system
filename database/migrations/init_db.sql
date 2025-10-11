-- 講座一覧テーブル
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL UNIQUE,
    note1 TEXT,
    note2 TEXT,
    note3 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 講座生徒名簿テーブル
CREATE TABLE IF NOT EXISTS course_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    student_number TEXT NOT NULL,
    class_number TEXT,
    student_name TEXT NOT NULL,
    note1 TEXT,
    note2 TEXT,
    note3 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE(course_id, student_number)
);

-- 成績入力テーブル
CREATE TABLE IF NOT EXISTS grade_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    entry_date DATE NOT NULL,
    student_number TEXT NOT NULL,
    grade1 INTEGER CHECK(grade1 IS NULL OR (grade1 >= 0 AND grade1 <= 4)),
    grade2 INTEGER CHECK(grade2 IS NULL OR (grade2 >= 0 AND grade2 <= 4)),
    grade3 INTEGER CHECK(grade3 IS NULL OR (grade3 >= 0 AND grade3 <= 4)),
    grade4 REAL,
    grade5 REAL,
    grade6 REAL,
    note1 TEXT,
    note2 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE(course_id, entry_date, student_number)
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_course_students_course ON course_students(course_id);
CREATE INDEX IF NOT EXISTS idx_grade_entries_course ON grade_entries(course_id);
CREATE INDEX IF NOT EXISTS idx_grade_entries_date ON grade_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_grade_entries_student ON grade_entries(student_number);

-- 成績一覧ビュー
CREATE VIEW IF NOT EXISTS grade_list_view AS
SELECT 
    ge.id,
    c.course_id,
    c.course_name,
    ge.entry_date,
    cs.student_number,
    cs.student_name,
    cs.class_number,
    ge.grade1,
    ge.grade2,
    ge.grade3,
    ge.grade4,
    ge.grade5,
    ge.grade6,
    ge.note1,
    ge.note2,
    ge.created_at,
    ge.updated_at
FROM grade_entries ge
JOIN courses c ON ge.course_id = c.course_id
JOIN course_students cs ON ge.course_id = cs.course_id 
    AND ge.student_number = cs.student_number
ORDER BY c.course_name, ge.entry_date, cs.student_number;
