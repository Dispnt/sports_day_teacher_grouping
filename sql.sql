CREATE DATABASE IF NOT EXISTS TeacherSports;
USE TeacherSports;
CREATE TABLE IF NOT EXISTS voting_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_name VARCHAR(255) NOT NULL,
    team VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO voting_records (teacher_name, team) VALUES
    ('张伟', 'blue'),
    ('张军', 'red');