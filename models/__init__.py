from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .user import User
from .project import Project
from .group import Group
from .group_member import GroupMember
from .activity import Activity
from .attendance import Attendance
from .missed_activity import MissedActivity
from .alert import Alert
