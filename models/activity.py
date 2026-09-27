from datetime import datetime
from models import db


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    scheduled_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(30), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship('Attendance', backref='activity_obj', lazy=True)
    missed_records = db.relationship('MissedActivity', backref='activity_obj', lazy=True)

    def __repr__(self):
        return f'<Activity {self.title}>'
