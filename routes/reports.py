from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required
from models import User, Project, Group, Activity, Attendance, MissedActivity, Alert
from routes import role_required

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports', methods=['GET'])
@login_required
@role_required('admin', 'instructor', 'project_leader')
def reports():
    students = User.query.filter_by(role='student').all()
    projects = Project.query.order_by(Project.project_name.asc()).all()
    groups = Group.query.order_by(Group.group_name.asc()).all()
    activity_types = ['weekly_meeting', 'proposal_submission', 'research_consultation']

    filters = {
        'student_id': request.args.get('student_id', ''),
        'group_id': request.args.get('group_id', ''),
        'project_id': request.args.get('project_id', ''),
        'activity_type': request.args.get('activity_type', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
    }

    report_rows = []
    for student in students:
        group_ids = [m.group_id for m in student.group_members if hasattr(student, 'group_members')]
        project_ids = [g.project_id for g in Group.query.filter(Group.id.in_(group_ids)).all()] if group_ids else []
        if filters['project_id'] and str(student_id := None) == '':
            pass
        if filters['group_id'] and not (str(filters['group_id']) in [str(gid) for gid in group_ids]):
            continue
        if filters['project_id'] and not (str(filters['project_id']) in [str(pid) for pid in project_ids]):
            continue

        activities = Activity.query.filter(Activity.group_id.in_(group_ids)).all() if group_ids else []
        if filters['activity_type']:
            activities = [a for a in activities if a.activity_type == filters['activity_type']]
        if filters['start_date']:
            activities = [a for a in activities if a.scheduled_date >= __import__('datetime').datetime.strptime(filters['start_date'], '%Y-%m-%d').date()]
        if filters['end_date']:
            activities = [a for a in activities if a.scheduled_date <= __import__('datetime').datetime.strptime(filters['end_date'], '%Y-%m-%d').date()]

        total = len(activities)
        present = Attendance.query.filter_by(student_id=student.id, attendance_status='Present').count()
        absent = Attendance.query.filter_by(student_id=student.id, attendance_status='Absent').count()
        percentage = round((present / total * 100), 2) if total else 0
        missed = MissedActivity.query.filter_by(student_id=student.id).count()

        if filters['student_id'] and str(student.id) != str(filters['student_id']):
            continue

        report_rows.append({
            'student': student,
            'project': Project.query.filter_by(id=project_ids[0]).first() if project_ids else None,
            'group': Group.query.filter_by(id=group_ids[0]).first() if group_ids else None,
            'total_activities': total,
            'present': present,
            'absent': absent,
            'percentage': percentage,
            'missed': missed,
        })

    return render_template(
        'reports.html',
        report_rows=report_rows,
        students=students,
        projects=projects,
        groups=groups,
        activity_types=activity_types,
        filters=filters
    )
