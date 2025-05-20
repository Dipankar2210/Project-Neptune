from app import db
from datetime import datetime

class KPIValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpi.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    kpi = db.relationship('KPI', back_populates='values')
    created_by = db.relationship('User', backref='kpi_values')

class KPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    due_date = db.Column(db.DateTime, nullable=False)
    benchmark_value = db.Column(db.Float, nullable=False)
    benchmark_calculation_method = db.Column(db.String(20), nullable=False, default='manual')  # manual, average
    benchmark_average_period = db.Column(db.String(20), nullable=True)  # 6_weeks, 9_weeks, yearly
    current_value = db.Column(db.Float, nullable=True)
    reminder = db.Column(db.String(20), nullable=True, default='none')
    status = db.Column(db.String(20), default='pending')  # pending, completed, at_risk
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    highlight_rule = db.Column(db.String(10), nullable=False, default='lt')

    project = db.relationship('Project', back_populates='kpis')
    values = db.relationship(
        'KPIValue',
        back_populates='kpi',
        order_by='desc(KPIValue.measurement_date)',
        cascade='all, delete-orphan'
    )

    @property
    def historical_values(self):
        """Return the last 10 values for the sparkline chart"""
        return [v.value for v in self.values[:10]]

    @property
    def current_value_nearest_today(self):
        """Return the KPI value with measurement_date nearest to today (server time)."""
        if not self.values:
            return None
        today = datetime.utcnow()
        nearest = min(self.values, key=lambda v: abs((v.measurement_date - today).total_seconds()))
        return nearest.value

    @property
    def historical_chart_data(self):
        """Return the last 10 (date, value) pairs for the sparkline chart."""
        return [
            {"date": v.measurement_date.strftime("%Y-%m-%d"), "value": v.value}
            for v in self.values[:10]
        ]

    def update_value(self, value, measurement_date, user_id):
        """Add a new KPI value and update current value"""
        kpi_value = KPIValue(
            kpi_id=self.id,
            value=value,
            measurement_date=measurement_date,
            created_by_id=user_id
        )
        db.session.add(kpi_value)
        self.current_value = value
        self.updated_at = datetime.utcnow()

        # Update status based on selected highlight_rule
        if self.is_at_risk(value):
            self.status = 'at_risk'
        elif value >= self.benchmark_value:
            self.status = 'completed'
        else:
            self.status = 'pending'

        db.session.commit()

    def is_at_risk(self, value):
        if self.highlight_rule == 'lt':
            return value < self.benchmark_value
        elif self.highlight_rule == 'gt':
            return value > self.benchmark_value
        elif self.highlight_rule == 'eq':
            return value == self.benchmark_value
        elif self.highlight_rule == 'le':
            return value <= self.benchmark_value
        elif self.highlight_rule == 'ge':
            return value >= self.benchmark_value
        elif self.highlight_rule == 'ne':
            return value != self.benchmark_value
        return False

    def __repr__(self):
        return f'<KPI {self.name}>'

class KPIUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpi.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20))  # red, yellow, green
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', backref='kpi_updates')
    
    def __repr__(self):
        return f'<KPIUpdate {self.id} for KPI {self.kpi_id}>' 