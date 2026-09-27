from datetime import datetime
from models import db


class GroupMember(db.Model):
    __tablename__ = 'group_members'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('group_id', 'student_id', name='unique_group_member'),
    )

    def __repr__(self):
        return f'<GroupMember group={self.group_id} student={self.student_id}>'
