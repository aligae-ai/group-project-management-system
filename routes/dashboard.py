from datetime import datetime
from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required
from models import db, User, GroupMember, Activity, Attendance, Alert, Project
from routes import role_required


dashboard_bp = Blueprint('dashboard', __name__)


def get_student_stats(student_id):
    memberships = GroupMember.query.filter_by(student_id=student_id).all()
    group_ids = [m.group_id for m in memberships]
    if not group_ids:
        return {'total_activities': 0, 'present': 0, 'absent': 0, 'percentage': 0, 'missed': 0, 'project_name': 'No Project Assigned'}

    activities = Activity.query.filter(Activity.group_id.in_(group_ids)).all()
    present = Attendance.query.filter_by(student_id=student_id, attendance_status='Present').count()
    absent = Attendance.query.filter_by(student_id=student_id, attendance_status='Absent').count()
    total_activities = len(activities)
    percentage = round((present / total_activities * 100), 2) if total_activities else 0
    missed = 0
    for item in activities:
        if Attendance.query.filter_by(activity_id=item.id, student_id=student_id, attendance_status='Absent').first():
            missed += 1
    project_name = Project.query.filter_by(id=activities[0].project_id).first().project_name if activities else 'No Project Assigned'
    return {
        'total_activities': total_activities,
        'present': present,
        'absent': absent,
        'percentage': percentage,
        'missed': missed,
        'project_name': project_name,
    }


@dashboard_bp.route('/dashboard')
@login_required
def index():
    student_group = GroupMember.query.filter_by(student_id=current_user.id).first()
    stats = get_student_stats(current_user.id)
    alerts = Alert.query.filter_by(student_id=current_user.id).order_by(Alert.created_at.desc()).all()
    upcoming = Activity.query.filter(Activity.group_id.in_([m.group_id for m in GroupMember.query.filter_by(student_id=current_user.id).all()])).order_by(Activity.scheduled_date.asc()).limit(5).all()

    return render_template(
        'dashboard.html',
        current_user=current_user,
        student_group=student_group,
        stats=stats,
        alerts=alerts,
        upcoming=upcoming,
        title='Dashboard'
    )
