from datetime import datetime
from models import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='active')

    groups = db.relationship('Group', backref='project_obj', lazy=True)
    activities = db.relationship('Activity', backref='project_obj', lazy=True)

    def __repr__(self):
        return f'<Project {self.project_name}>'
