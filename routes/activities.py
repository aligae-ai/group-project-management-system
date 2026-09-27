from datetime import datetime
from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

from models import db, Activity, Project, Group, GroupMember, User
from routes import role_required

activities_bp = Blueprint('activities', __name__)


class ActivityForm(FlaskForm):
    project_id = SelectField('Project', validators=[DataRequired()], coerce=int)
    group_id = SelectField('Group', validators=[DataRequired()], coerce=int)
    activity_type = SelectField('Activity Type', choices=[
        ('weekly_meeting', 'Weekly Meeting'),
        ('proposal_submission', 'Proposal Submission'),
        ('research_consultation', 'Research Consultation')
    ], validators=[DataRequired()])
    title = StringField('Activity Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    scheduled_date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])
    location = StringField('Location or Meeting Link', validators=[Optional()])
    submit = SubmitField('Save Activity')


@activities_bp.route('/activities', methods=['GET'])
@login_required
def list_activities():
    group_ids = [m.group_id for m in GroupMember.query.filter_by(student_id=current_user.id).all()]
    if current_user.role in ['admin', 'instructor']:
        activities = Activity.query.order_by(Activity.scheduled_date.asc()).all()
    elif current_user.role == 'project_leader':
        groups = Group.query.filter_by(leader_id=current_user.id).all()
        group_ids = [g.id for g in groups]
        activities = Activity.query.filter(Activity.group_id.in_(group_ids)).order_by(Activity.scheduled_date.asc()).all()
    else:
        activities = Activity.query.filter(Activity.group_id.in_(group_ids)).order_by(Activity.scheduled_date.asc()).all() if group_ids else []
    return render_template('activities.html', activities=activities)


@activities_bp.route('/activities/create', methods=['GET', 'POST'])
@login_required
@role_required('project_leader', 'admin', 'instructor')
def create_activity():
    form = ActivityForm()
    form.project_id.choices = [(p.id, p.project_name) for p in Project.query.order_by(Project.project_name.asc()).all()]
    form.group_id.choices = [(g.id, g.group_name) for g in Group.query.order_by(Group.group_name.asc()).all()]

    if form.validate_on_submit():
        new_activity = Activity(
            project_id=form.project_id.data,
            group_id=form.group_id.data,
            activity_type=form.activity_type.data,
            title=form.title.data,
            description=form.description.data,
            scheduled_date=form.scheduled_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            created_by=current_user.id,
            status='scheduled'
        )
        db.session.add(new_activity)
        db.session.commit()
        flash('Activity created successfully.', 'success')
        return redirect(url_for('activities.list_activities'))
    return render_template('activities.html', form=form, is_create=True)


@activities_bp.route('/activities/<int:id>')
@login_required
def view_activity(id):
    activity = Activity.query.get_or_404(id)
    group = Group.query.get(activity.group_id)
    project = Project.query.get(activity.project_id)
    members = GroupMember.query.filter_by(group_id=activity.group_id).all()
    return render_template('activities.html', activity=activity, group=group, project=project, members=members)
