from celery import Celery
from app import db
from app.models.kpi import KPI
from datetime import datetime, timedelta

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def calculate_benchmark_average(kpi_id):
    """Calculate the benchmark average for a KPI based on its period."""
    kpi = KPI.query.get(kpi_id)
    if not kpi or kpi.benchmark_calculation_method != 'average':
        return

    # Get the date range based on the period
    end_date = datetime.utcnow()
    if kpi.benchmark_average_period == '6_weeks':
        start_date = end_date - timedelta(weeks=6)
    elif kpi.benchmark_average_period == '9_weeks':
        start_date = end_date - timedelta(weeks=9)
    else:  # yearly
        start_date = end_date - timedelta(days=365)

    # Get all KPI values within the date range
    values = [v.value for v in kpi.values 
             if start_date <= v.measurement_date <= end_date]

    if values:
        # Calculate the average
        average = sum(values) / len(values)
        
        # Update the KPI's benchmark value
        kpi.benchmark_value = average
        db.session.commit() 