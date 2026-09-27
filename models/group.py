from datetime import datetime
from models import db


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    group_name = db.Column(db.String(200), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('GroupMember', backref='group_obj', lazy=True)
    activities = db.relationship('Activity', backref='group_obj', lazy=True)

    def __repr__(self):
        return f'<Group {self.group_name}>'
