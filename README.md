# Group Project Management System

This project is a Flask-based web application for managing group projects, scheduled activities, attendance, missed activities, accountability alerts, and reports for Information Technology students.

## Features
- Role-based login for Student, Project Leader, Instructor/Adviser, and Administrator
- Group and project management
- Scheduled activity creation and listing
- Automatic attendance decisions using the flowchart logic
- Missed activity classification and tracking
- Accountability alerts on the student dashboard
- Attendance percentage recalculation from stored attendance records
- MySQL-backed persistence
- Dashboard and reports for monitoring student performance

## Project Structure
- `app.py` - app entry point
- `config.py` - configuration and environment settings
- `database.sql` - MySQL schema and sample data template
- `models/` - SQLAlchemy models
- `routes/` - Flask route modules
- `templates/` - HTML templates
- `static/` - CSS and JavaScript assets

## Requirements
- Python 3.10+
- MySQL Server / MySQL Workbench
- Visual Studio Code or Visual Studio with Python support

## Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the MySQL database and import schema:
   ```sql
   CREATE DATABASE group_project_management;
   ```
   Then import `database.sql` through MySQL Workbench or CLI.

4. Configure environment variables:
   ```bash
   copy .env.example .env
   ```
   Update `.env` with your local database credentials.

5. Run the app:
   ```bash
   python app.py
   ```

6. Open the site in your browser:
   ```text
   http://localhost:5000/login
   ```

## Default sample users
The app seeds sample users on first startup if they do not already exist.

- Admin: admin@groupproject.com / Admin123!
- Instructor: instructor@groupproject.com / Instructor123!
- Project Leader: john@groupproject.com / Leader123!
- Student: student1a@groupproject.com / Student1123!

## MySQL configuration
Edit `.env`:
```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=group_project_management
```

## Important workflow implemented
The application follows the flowchart logic:
1. Scheduled activity is created.
2. Attendance is checked for each member.
3. If present, attendance is recorded and the dashboard updates.
4. If absent, a missed activity record is created.
5. The activity category is identified and stored.
6. An accountability alert is generated.
7. Attendance percentage is recalculated automatically.
8. Dashboard counters and alerts are updated.

## Notes
This project is designed as a beginner-friendly capstone project and is intentionally structured for academic learning and demonstration.
