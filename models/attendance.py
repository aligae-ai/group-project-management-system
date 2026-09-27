from datetime import datetime
from models import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendance_status = db.Column(db.String(20), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint('activity_id', 'student_id', name='unique_activity_student'),
    )

    def __repr__(self):
        return f'<Attendance activity={self.activity_id} student={self.student_id} status={self.attendance_status}>'
