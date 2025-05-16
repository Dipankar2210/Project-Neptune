from app import db
from datetime import datetime

# Association table for project team members
project_team = db.Table('project_team',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    team_size = db.Column(db.Integer, nullable=False)
    monthly_cost = db.Column(db.Float, nullable=False)  # in USD
    yearly_cost = db.Column(db.Float, nullable=False)   # in USD
    project_type = db.Column(db.String(50), nullable=False)  # Fixed cost, Time and Material, Staff Augmentation, Support
    status = db.Column(db.String(20), default='active')  # active, completed, on-hold, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_projects')
    project_manager = db.relationship('User', foreign_keys=[project_manager_id], backref='managed_projects')
    team_members = db.relationship('User', secondary=project_team, backref='assigned_projects')
    kpis = db.relationship('KPI', back_populates='project')
    
    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)
        # Calculate yearly cost based on monthly cost
        self.yearly_cost = self.monthly_cost * 12
    
    def __repr__(self):
        return f'<Project {self.name}>' 