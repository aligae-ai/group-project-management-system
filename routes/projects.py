from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_login import current_user, login_required
from models import db, Project, Group, GroupMember, User
from routes import role_required

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
@login_required
def list_projects():
    if current_user.role in ['admin', 'instructor']:
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        memberships = GroupMember.query.filter_by(student_id=current_user.id).all()
        group_ids = [m.group_id for m in memberships]
        projects = []
        if group_ids:
            groups = Group.query.filter(Group.id.in_(group_ids)).all()
            project_ids = [g.project_id for g in groups]
            projects = Project.query.filter(Project.id.in_(project_ids)).all()
    return render_template('projects.html', projects=projects)


@projects_bp.route('/projects/<int:id>')
@login_required
def project_detail(id):
    project = Project.query.get_or_404(id)
    groups = Group.query.filter_by(project_id=id).all()
    return render_template('project_details.html', project=project, groups=groups)
