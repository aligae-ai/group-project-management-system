from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from models import db, Attendance, Activity, Group, GroupMember, User, MissedActivity, Alert, Project
from routes import role_required

attendance_bp = Blueprint('attendance', __name__)


class AttendanceForm(FlaskForm):
    activity_id = SelectField('Activity', validators=[DataRequired()], coerce=int)
    student_id = SelectField('Student', validators=[DataRequired()], coerce=int)
    attendance_status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Excused', 'Excused')], validators=[DataRequired()])
    remarks = TextAreaField('Remarks', validators=[Optional()])
    submit = SubmitField('Save Attendance')


def recalculate_student_attendance(student_id):
    memberships = GroupMember.query.filter_by(student_id=student_id).all()
    group_ids = [m.group_id for m in memberships]
    if not group_ids:
        return 0
    activities = Activity.query.filter(Activity.group_id.in_(group_ids)).all()
    total = len(activities)
    present = Attendance.query.filter_by(student_id=student_id, attendance_status='Present').count()
    if total == 0:
        return 0
    return round((present / total) * 100, 2)


def process_attendance(activity_id, student_id, status, remarks=''):
    activity = Activity.query.get_or_404(activity_id)
    existing = Attendance.query.filter_by(activity_id=activity_id, student_id=student_id).first()
    if existing:
        existing.attendance_status = status
        existing.recorded_at = datetime.utcnow()
        existing.remarks = remarks
        attendance_record = existing
    else:
        attendance_record = Attendance(
            activity_id=activity_id,
            student_id=student_id,
            attendance_status=status,
            remarks=remarks
        )
        db.session.add(attendance_record)

    if status == 'Absent':
        missed = MissedActivity.query.filter_by(activity_id=activity_id, student_id=student_id).first()
        if not missed:
            missed_item = MissedActivity(
                activity_id=activity_id,
                student_id=student_id,
                project_id=activity.project_id,
                activity_type=activity.activity_type,
                reason=remarks or 'Missed scheduled activity',
                date_missed=activity.scheduled_date,
            )
            db.session.add(missed_item)

        alert_message = (
            f"You missed a scheduled {activity.activity_type.replace('_', ' ')} on {activity.scheduled_date}. "
            f"Your attendance percentage has been updated."
        )

        alert = Alert.query.filter_by(student_id=student_id, activity_id=activity_id).first()
        if not alert:
            alert = Alert(student_id=student_id, activity_id=activity_id, alert_type=activity.activity_type, message=alert_message)
            db.session.add(alert)

    if status == 'Present':
        missed = MissedActivity.query.filter_by(activity_id=activity_id, student_id=student_id).first()
        if missed:
            db.session.delete(missed)

    if status == 'Excused':
        missed = MissedActivity.query.filter_by(activity_id=activity_id, student_id=student_id).first()
        if missed:
            db.session.delete(missed)

    calc = recalculate_student_attendance(student_id)
    db.session.commit()
    return {'status': status, 'percentage': calc, 'record': attendance_record}


@attendance_bp.route('/attendance', methods=['GET'])
@login_required
def list_attendance():
    if current_user.role in ['admin', 'instructor']:
        records = Attendance.query.order_by(Attendance.recorded_at.desc()).all()
    elif current_user.role == 'project_leader':
        my_groups = Group.query.filter_by(leader_id=current_user.id).all()
        group_ids = [g.id for g in my_groups]
        records = []
        for group_id in group_ids:
            group_members = [gm.student_id for gm in GroupMember.query.filter_by(group_id=group_id).all()]
            if group_members:
                records.extend(Attendance.query.filter(Attendance.student_id.in_(group_members)).all())
    else:
        records = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.recorded_at.desc()).all()
    return render_template('attendance.html', records=records)


@attendance_bp.route('/attendance/record', methods=['GET', 'POST'])
@login_required
@role_required('project_leader', 'admin', 'instructor')
def record_attendance():
    form = AttendanceForm()
    form.activity_id.choices = [(a.id, f'{a.title} ({a.activity_type})') for a in Activity.query.order_by(Activity.scheduled_date.asc()).all()]

    if current_user.role == 'project_leader':
        group_ids = [g.id for g in Group.query.filter_by(leader_id=current_user.id).all()]
        members = User.query.join(GroupMember, User.id == GroupMember.student_id).filter(GroupMember.group_id.in_(group_ids)).all()
    else:
        members = User.query.filter_by(role='student').all()
    form.student_id.choices = [(u.id, u.full_name) for u in members]

    if form.validate_on_submit():
        try:
            result = process_attendance(form.activity_id.data, form.student_id.data, form.attendance_status.data, form.remarks.data or '')
            flash(f'Attendance saved successfully. Updated percentage: {result["percentage"]}%.', 'success')
            return redirect(url_for('attendance.list_attendance'))
        except Exception as e:
            flash(f'Unable to save attendance: {e}', 'danger')

    return render_template('attendance.html', form=form, is_record=True)
