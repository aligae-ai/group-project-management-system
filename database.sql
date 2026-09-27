CREATE DATABASE IF NOT EXISTS group_project_management;
USE group_project_management;

DROP TABLE IF EXISTS accountability_alerts;
DROP TABLE IF EXISTS missed_activities;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS group_members;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_number VARCHAR(50) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(200) NOT NULL,
    description TEXT,
    instructor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) DEFAULT 'active',
    CONSTRAINT fk_projects_instructor FOREIGN KEY (instructor_id) REFERENCES users(id)
);

CREATE TABLE groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    group_name VARCHAR(200) NOT NULL,
    leader_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_groups_project FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT fk_groups_leader FOREIGN KEY (leader_id) REFERENCES users(id)
);

CREATE TABLE group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    student_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_group_member (group_id, student_id),
    CONSTRAINT fk_group_members_group FOREIGN KEY (group_id) REFERENCES groups(id),
    CONSTRAINT fk_group_members_student FOREIGN KEY (student_id) REFERENCES users(id)
);

CREATE TABLE activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    group_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    location VARCHAR(255),
    created_by INT NOT NULL,
    status VARCHAR(30) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activities_project FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT fk_activities_group FOREIGN KEY (group_id) REFERENCES groups(id),
    CONSTRAINT fk_activities_creator FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_id INT NOT NULL,
    student_id INT NOT NULL,
    attendance_status VARCHAR(20) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    UNIQUE KEY unique_activity_student (activity_id, student_id),
    CONSTRAINT fk_attendance_activity FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_id) REFERENCES users(id)
);

CREATE TABLE missed_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_id INT NOT NULL,
    student_id INT NOT NULL,
    project_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    reason TEXT,
    date_missed DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_missed_activity FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT fk_missed_student FOREIGN KEY (student_id) REFERENCES users(id),
    CONSTRAINT fk_missed_project FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE accountability_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    activity_id INT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alert_student FOREIGN KEY (student_id) REFERENCES users(id),
    CONSTRAINT fk_alert_activity FOREIGN KEY (activity_id) REFERENCES activities(id)
);

INSERT INTO users (student_number, first_name, last_name, email, password_hash, role)
VALUES
('ADM-001', 'System', 'Administrator', 'admin@groupproject.com', 'change-me', 'admin'),
('INS-001', 'Maria', 'Santos', 'instructor@groupproject.com', 'change-me', 'instructor'),
('2023-001', 'John', 'Delos Reyes', 'john@groupproject.com', 'change-me', 'project_leader'),
('2023-002', 'Alyssa', 'Velasco', 'alyssa@groupproject.com', 'change-me', 'project_leader'),
('2023-101', 'Student1', 'A', 'student1a@groupproject.com', 'change-me', 'student'),
('2023-102', 'Student2', 'A', 'student2a@groupproject.com', 'change-me', 'student'),
('2023-103', 'Student3', 'A', 'student3a@groupproject.com', 'change-me', 'student'),
('2023-104', 'Student4', 'A', 'student4a@groupproject.com', 'change-me', 'student'),
('2023-105', 'Student5', 'A', 'student5a@groupproject.com', 'change-me', 'student'),
('2023-106', 'Student6', 'A', 'student6a@groupproject.com', 'change-me', 'student');

INSERT INTO projects (project_name, description, instructor_id, status)
VALUES
('IT Project Management System', 'A group project for managing workload and attendance.', 2, 'active'),
('Smart Campus Monitoring', 'A monitoring system for attendance and campus activities.', 2, 'active');

INSERT INTO groups (project_id, group_name, leader_id)
VALUES
(1, 'Team Alpha', 3),
(2, 'Team Beta', 4);

INSERT INTO group_members (group_id, student_id)
VALUES
(1, 3), (1, 5), (1, 6), (1, 7), (1, 8),
(2, 4), (2, 9), (2, 10), (2, 11);

INSERT INTO activities (project_id, group_id, activity_type, title, description, scheduled_date, start_time, end_time, location, created_by, status)
VALUES
(1, 1, 'weekly_meeting', 'Sprint Planning', 'Weekly sprint planning and task updates.', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00:00', '10:00:00', 'Room 302', 3, 'scheduled'),
(1, 1, 'proposal_submission', 'Proposal Draft Submission', 'Submission of the project proposal draft.', DATE_ADD(CURDATE(), INTERVAL 2 DAY), '13:00:00', '14:00:00', 'Google Classroom', 3, 'scheduled'),
(2, 2, 'research_consultation', 'Research Consultation', 'Consultation with adviser about project research.', DATE_ADD(CURDATE(), INTERVAL 3 DAY), '11:00:00', '12:00:00', 'Adviser Office', 4, 'scheduled');

INSERT INTO attendance (activity_id, student_id, attendance_status, remarks)
VALUES
(1, 3, 'Present', 'Weekly meeting attended'),
(1, 5, 'Present', 'Attendance taken'),
(1, 6, 'Absent', 'No attendance recorded'),
(1, 7, 'Present', 'Attendance taken'),
(1, 8, 'Present', 'Attendance taken');

INSERT INTO missed_activities (activity_id, student_id, project_id, activity_type, reason, date_missed)
VALUES
(1, 6, 1, 'weekly_meeting', 'Missed weekly meeting', DATE_ADD(CURDATE(), INTERVAL 1 DAY));

INSERT INTO accountability_alerts (student_id, activity_id, alert_type, message, is_read)
VALUES
(6, 1, 'weekly_meeting', 'You missed a scheduled weekly group meeting. Your attendance percentage has been updated.', FALSE);
