from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.kpi import KPI, KPIValue
from app.models.project import Project
from app.models.user import User
from app import db
from app.controllers.auth import role_required
from datetime import datetime
from app.tasks import calculate_benchmark_average

kpi_bp = Blueprint('kpi', __name__)

@kpi_bp.route('/kpis')
@login_required
def list_kpis():
    if current_user.role == 'admin':
        # Admin can see all KPIs
        kpis = KPI.query.all()
    elif current_user.role == 'project_manager':
        # Project managers can see KPIs for projects they manage
        managed_projects = Project.query.filter_by(project_manager_id=current_user.id).all()
        project_ids = [project.id for project in managed_projects]
        kpis = KPI.query.filter(KPI.project_id.in_(project_ids)).all()
    else:
        # Team members can see KPIs assigned to them
        kpis = KPI.query.filter_by(assigned_to_id=current_user.id).all()
    
    return render_template('kpi/list.html', kpis=kpis)

@kpi_bp.route('/kpis/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'project_manager')
def create_kpi():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            project_id = request.form.get('project_id')
            unit = request.form.get('unit')
            frequency = request.form.get('frequency')
            due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
            benchmark_calculation_method = request.form.get('benchmark_calculation_method')
            benchmark_average_period = request.form.get('benchmark_average_period')
            
            # Handle benchmark value based on calculation method
            if benchmark_calculation_method == 'manual':
                benchmark_value = float(request.form.get('benchmark_value'))
            else:  # average
                # For now, we'll set a default value and update it later
                benchmark_value = 0.0
                # Note: The actual average calculation will be done in a background task
                # or when the KPI is first viewed
            
            current_value = float(request.form.get('current_value'))
            assigned_to_id = request.form.get('assigned_to_id')

            # Create new KPI
            kpi = KPI(
                name=name,
                description=description,
                project_id=project_id,
                unit=unit,
                frequency=frequency,
                due_date=due_date,
                benchmark_value=benchmark_value,
                benchmark_calculation_method=benchmark_calculation_method,
                benchmark_average_period=benchmark_average_period,
                current_value=current_value,
                assigned_to_id=assigned_to_id if assigned_to_id else None
            )

            db.session.add(kpi)
            db.session.commit()

            # Add initial KPI value
            kpi_value = KPIValue(
                kpi_id=kpi.id,
                value=current_value,
                measurement_date=datetime.utcnow(),
                created_by_id=current_user.id
            )
            db.session.add(kpi_value)
            db.session.commit()

            # If using average calculation, trigger the calculation
            if benchmark_calculation_method == 'average':
                calculate_benchmark_average.delay(kpi.id)

            flash('KPI created successfully!', 'success')
            return redirect(url_for('kpi.list_kpis'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating KPI: {str(e)}', 'error')

    # Get projects and team members for the form
    if current_user.role == 'admin':
        projects = Project.query.all()
        team_members = User.query.filter(User.role.in_(['team_member', 'project_manager'])).all()
    else:
        # Project managers can only select from their managed projects
        projects = Project.query.filter_by(project_manager_id=current_user.id).all()
        team_members = []
        for project in projects:
            team_members.extend(project.team_members)
        team_members = list(set(team_members))  # Remove duplicates

    return render_template('kpi/create.html', projects=projects, team_members=team_members)

@kpi_bp.route('/kpis/<int:kpi_id>/update_value', methods=['POST'])
@login_required
def update_value(kpi_id):
    kpi = KPI.query.get_or_404(kpi_id)
    
    # Check if user has permission to update the KPI
    if not (current_user.role in ['admin', 'project_manager'] or current_user.id == kpi.assigned_to_id):
        flash('You do not have permission to update this KPI.', 'error')
        return redirect(url_for('project.view_project', project_id=kpi.project_id))
    
    try:
        new_value = float(request.form.get('new_value'))
        measurement_date = datetime.strptime(request.form.get('measurement_date'), '%Y-%m-%d')
        
        # Check if the update frequency is allowed
        last_update = kpi.values[0] if kpi.values else None
        if last_update:
            # if kpi.frequency == 'daily' and (measurement_date - last_update.measurement_date).days < 1:
            #     flash('Daily KPIs can only be updated once per day.', 'error')
            #     return redirect(url_for('project.view_project', project_id=kpi.project_id))
            # elif kpi.frequency == 'weekly' and (measurement_date - last_update.measurement_date).days < 7:
            #     flash('Weekly KPIs can only be updated once per week.', 'error')
            #     return redirect(url_for('project.view_project', project_id=kpi.project_id))
            # elif kpi.frequency == 'monthly' and (measurement_date - last_update.measurement_date).days < 30:
            #     flash('Monthly KPIs can only be updated once per month.', 'error')
            #     return redirect(url_for('project.view_project', project_id=kpi.project_id))
            # elif kpi.frequency == 'quarterly' and (measurement_date - last_update.measurement_date).days < 90:
            #     flash('Quarterly KPIs can only be updated once per quarter.', 'error')
            #     return redirect(url_for('project.view_project', project_id=kpi.project_id))
            # elif kpi.frequency == 'yearly' and (measurement_date - last_update.measurement_date).days < 365:
            #     flash('Yearly KPIs can only be updated once per year.', 'error')
            #     return redirect(url_for('project.view_project', project_id=kpi.project_id))
            pass
        
        kpi.update_value(new_value, measurement_date, current_user.id)
        flash('KPI value updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating KPI value: {str(e)}', 'error')
    
    return redirect(url_for('project.view_project', project_id=kpi.project_id))

@kpi_bp.route('/kpis/<int:kpi_id>/edit', methods=['POST'])
@login_required
@role_required('admin', 'project_manager')
def edit_kpi(kpi_id):
    kpi = KPI.query.get_or_404(kpi_id)
    try:
        kpi.name = request.form.get('name')
        kpi.description = request.form.get('description')
        kpi.unit = request.form.get('unit')
        kpi.benchmark_value = float(request.form.get('benchmark_value'))
        kpi.frequency = request.form.get('frequency')
        kpi.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        db.session.commit()
        flash('KPI updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating KPI: {str(e)}', 'error')
    return redirect(url_for('project.view_project', project_id=kpi.project_id))

@kpi_bp.route('/kpis/<int:kpi_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'project_manager')
def delete_kpi(kpi_id):
    kpi = KPI.query.get_or_404(kpi_id)
    project_id = kpi.project_id
    try:
        db.session.delete(kpi)
        db.session.commit()
        flash('KPI deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting KPI: {str(e)}', 'error')
    return redirect(url_for('project.view_project', project_id=project_id))

@kpi_bp.route('/kpis/<int:kpi_id>')
@login_required
def kpi_detail(kpi_id):
    kpi = KPI.query.get_or_404(kpi_id)
    return render_template('kpi/detail.html', kpi=kpi)

@kpi_bp.route('/kpi_values/<int:value_id>/edit', methods=['POST'])
@login_required
@role_required('admin', 'project_manager')
def edit_kpi_value(value_id):
    value = KPIValue.query.get_or_404(value_id)
    kpi_id = value.kpi_id
    try:
        value.value = float(request.form.get('value'))
        value.measurement_date = datetime.strptime(request.form.get('measurement_date'), '%Y-%m-%d')
        db.session.commit()
        flash('KPI value updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating KPI value: {str(e)}', 'error')
    return redirect(url_for('kpi.kpi_detail', kpi_id=kpi_id))

@kpi_bp.route('/kpi_values/<int:value_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'project_manager')
def delete_kpi_value(value_id):
    value = KPIValue.query.get_or_404(value_id)
    kpi_id = value.kpi_id
    try:
        db.session.delete(value)
        db.session.commit()
        flash('KPI value deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting KPI value: {str(e)}', 'error')
    return redirect(url_for('kpi.kpi_detail', kpi_id=kpi_id)) 