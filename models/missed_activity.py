from datetime import datetime
from models import db


class MissedActivity(db.Model):
    __tablename__ = 'missed_activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text)
    date_missed = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MissedActivity student={self.student_id} type={self.activity_type}>'
