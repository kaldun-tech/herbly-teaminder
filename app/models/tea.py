"""Tea model for PostgreSQL"""
from datetime import datetime
from app.extensions import db

class Tea(db.Model):
    """Tea model"""
    __tablename__ = 'teas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    steep_time = db.Column(db.Integer, nullable=False)  # in seconds
    steep_temperature = db.Column(db.Integer, nullable=False)  # in celsius
    steep_count = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

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
