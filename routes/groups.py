from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models import db, Group, GroupMember, User
from routes import role_required


groups_bp = Blueprint('groups', __name__)


@groups_bp.route('/groups')
@login_required
def list_groups():
    if current_user.role in ['admin', 'instructor']:
        groups = Group.query.order_by(Group.created_at.desc()).all()
    else:
        group_ids = [m.group_id for m in GroupMember.query.filter_by(student_id=current_user.id).all()]
        groups = Group.query.filter(Group.id.in_(group_ids)).all() if group_ids else []
    return render_template('groups.html', groups=groups)


@groups_bp.route('/groups/<int:id>')
@login_required
def group_detail(id):
    group = Group.query.get_or_404(id)
    members = []
    for gm in GroupMember.query.filter_by(group_id=id).all():
        member = User.query.get(gm.student_id)
        if member:
            members.append(member)
    return render_template('groups.html', group=group, members=members)
