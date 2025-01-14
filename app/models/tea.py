"""Tea model for PostgreSQL"""
from datetime import datetime, timezone
from app.extensions import db

# pylint: disable=too-many-instance-attributes
class Tea(db.Model):
    """Tea model"""
    __tablename__ = 'teas'

    id = db.Column(db.Integer, primary_key=True)  # pylint: disable=no-member
    name = db.Column(db.String(100), unique=True, nullable=False)  # pylint: disable=no-member
    type = db.Column(db.String(50), nullable=False)  # pylint: disable=no-member
    steep_time = db.Column(db.Integer, nullable=False)  # in seconds  # pylint: disable=no-member
    steep_temperature = db.Column(db.Integer, nullable=False)  # in celsius  # pylint: disable=no-member
    steep_count = db.Column(db.Integer, default=0)  # pylint: disable=no-member
    notes = db.Column(db.Text)  # pylint: disable=no-member
    created_at = db.Column(db.DateTime, nullable=False,
                          default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))  # pylint: disable=no-member
    updated_at = db.Column(db.DateTime, nullable=False,
                          default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
                          onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))  # pylint: disable=no-member
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # pylint: disable=no-member

    def __init__(self, name=None, type=None, steep_time=None, steep_temperature=None,
                notes=None, user_id=None, steep_count=None, created_at=None, updated_at=None):
        """Initialize tea"""
        self.name = name
        self.type = type
        self.steep_time = steep_time
        self.steep_temperature = steep_temperature
        self.notes = notes
        self.user_id = user_id
        self.steep_count = steep_count if steep_count is not None else 0
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        self.created_at = created_at if created_at is not None else now
        self.updated_at = updated_at if updated_at is not None else now

    def to_dict(self):
        """Convert tea to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'steep_time': self.steep_time,
            'steep_temperature': self.steep_temperature,
            'steep_count': self.steep_count,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Tea {self.name}>'
