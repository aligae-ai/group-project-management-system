from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.projects import projects_bp
from routes.groups import groups_bp
from routes.activities import activities_bp
from routes.attendance import attendance_bp
from routes.reports import reports_bp

login_manager = LoginManager()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    csrf.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()
        seed_sample_data()

    return app


def seed_sample_data():
    """Create default test users and sample records when the database is empty."""
    from models import User, Project, Group, GroupMember, Activity, Attendance, MissedActivity, Alert
    from datetime import datetime, timedelta
    from werkzeug.security import generate_password_hash

    admin = User.query.filter_by(email='admin@groupproject.com').first()
    if not admin:
        admin = User(
            student_number='ADM-001',
            first_name='System',
            last_name='Administrator',
            email='admin@groupproject.com',
            role='admin',
            password_hash=generate_password_hash('Admin123!')
        )
        db.session.add(admin)
        db.session.flush()

    instructor = User.query.filter_by(email='instructor@groupproject.com').first()
    if not instructor:
        instructor = User(
            student_number='INS-001',
            first_name='Maria',
            last_name='Santos',
            email='instructor@groupproject.com',
            role='instructor',
            password_hash=generate_password_hash('Instructor123!')
        )
        db.session.add(instructor)
        db.session.flush()

    project_count = Project.query.count()
    if project_count == 0:
        project1 = Project(project_name='IT Project Management System', description='A group project for managing workload and attendance.', instructor_id=instructor.id, status='active')
        project2 = Project(project_name='Smart Campus Monitoring', description='A system for campus activity tracking and attendance analytics.', instructor_id=instructor.id, status='active')
        db.session.add_all([project1, project2])
        db.session.flush()

        leader1 = User(
            student_number='2023-001',
            first_name='John',
            last_name='Delos Reyes',
            email='john@groupproject.com',
            role='project_leader',
            password_hash=generate_password_hash('Leader123!')
        )
        leader2 = User(
            student_number='2023-002',
            first_name='Alyssa',
            last_name='Velasco',
            email='alyssa@groupproject.com',
            role='project_leader',
            password_hash=generate_password_hash('Leader456!')
        )
        db.session.add_all([leader1, leader2])
        db.session.flush()

        students = [
            User(student_number=f'2023-{100+i}', first_name=f'Student{i}', last_name='A', email=f'student{i}a@groupproject.com', role='student', password_hash=generate_password_hash(f'Student{i}123!'))
            for i in range(1, 9)
        ]
        db.session.add_all(students)
        db.session.flush()

        student_list = [leader1, leader2] + students

        group1 = Group(project_id=project1.id, group_name='Team Alpha', leader_id=leader1.id)
        group2 = Group(project_id=project2.id, group_name='Team Beta', leader_id=leader2.id)
        db.session.add_all([group1, group2])
        db.session.flush()

        for student in student_list[:5]:
            db.session.add(GroupMember(group_id=group1.id, student_id=student.id))
        for student in student_list[5:]:
            db.session.add(GroupMember(group_id=group2.id, student_id=student.id))

        today = datetime.utcnow().date()
        activity1 = Activity(project_id=project1.id, group_id=group1.id, activity_type='weekly_meeting', title='Sprint Planning', description='Planning the weekly project tasks.', scheduled_date=today + timedelta(days=1), start_time='09:00:00', end_time='10:00:00', location='Room 302', created_by=leader1.id, status='scheduled')
        activity2 = Activity(project_id=project1.id, group_id=group1.id, activity_type='proposal_submission', title='Proposal Draft Submission', description='Final proposal check and submission.', scheduled_date=today + timedelta(days=2), start_time='13:00:00', end_time='14:00:00', location='Google Classroom', created_by=leader1.id, status='scheduled')
        activity3 = Activity(project_id=project2.id, group_id=group2.id, activity_type='research_consultation', title='Research Consultation', description='Consultation with adviser.', scheduled_date=today + timedelta(days=3), start_time='11:00:00', end_time='12:00:00', location='Adviser Office', created_by=leader2.id, status='scheduled')
        db.session.add_all([activity1, activity2, activity3])
        db.session.flush()

        for member in GroupMember.query.filter_by(group_id=group1.id).all():
            status = 'Present' if member.student_id != students[0].id else 'Absent'
            db.session.add(Attendance(activity_id=activity1.id, student_id=member.student_id, attendance_status=status, remarks='Recorded by leader'))
            if member.student_id == students[0].id:
                db.session.add(MissedActivity(activity_id=activity1.id, student_id=member.student_id, project_id=project1.id, activity_type='weekly_meeting', reason='Missed weekly meeting', date_missed=activity1.scheduled_date))
                db.session.add(Alert(student_id=member.student_id, activity_id=activity1.id, alert_type='weekly_meeting', message=f'You missed a scheduled weekly group meeting on {activity1.scheduled_date}. Your attendance percentage has been updated.', is_read=False))

        # Add one more attended activity for project2
        group2_members = GroupMember.query.filter_by(group_id=group2.id).all()
        for member in group2_members:
            db.session.add(Attendance(activity_id=activity3.id, student_id=member.student_id, attendance_status='Present', remarks='Consultation attended'))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
