from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.kpi import KPI
from app.models.user import User
from app import db
from app.controllers.auth import role_required
from datetime import datetime

project_bp = Blueprint('project', __name__)

@project_bp.route('/projects')
@login_required
def list_projects():
    if current_user.role == 'admin':
        # Admin can see all projects
        projects = Project.query.all()
    elif current_user.role == 'project_manager':
        # Project managers can see projects they're managing and assigned to
        managed_projects = Project.query.filter_by(project_manager_id=current_user.id).all()
        assigned_projects = current_user.assigned_projects
        # Combine both sets of projects, removing duplicates
        projects = list(set(managed_projects + assigned_projects))
    else:
        # Other users can see projects they're assigned to
        projects = current_user.assigned_projects
    
    return render_template('project/list.html', projects=projects)

@project_bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'project_manager')
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        team_size = request.form.get('team_size')
        monthly_cost = request.form.get('monthly_cost')
        project_type = request.form.get('project_type')
        status = request.form.get('status')
        team_member_ids = request.form.getlist('team_members')
        
        try:
            project = Project(
                name=name,
                description=description,
                team_size=int(team_size),
                monthly_cost=float(monthly_cost),
                project_type=project_type,
                status=status,
                created_by_id=current_user.id,
                project_manager_id=current_user.id  # Automatically assign current user as project manager
            )
            
            # Add team members
            if team_member_ids:
                team_members = User.query.filter(User.id.in_(team_member_ids)).all()
                project.team_members.extend(team_members)
            
            db.session.add(project)
            db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('project.list_projects'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
    
    # Get all active users for resource allocation
    users = User.query.filter_by(status='active').all()
    return render_template('project/create.html', users=users)

@project_bp.route('/projects/<int:project_id>', methods=['GET', 'POST'])
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    if not (current_user.role == 'admin' or 
            current_user.id == project.project_manager_id or 
            current_user in project.team_members):
        flash('You do not have permission to view this project.', 'error')
        return redirect(url_for('project.list_projects'))

    # Handle KPI creation
    if request.method == 'POST' and current_user.role in ['admin', 'project_manager']:
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            unit = request.form.get('unit')
            frequency = request.form.get('frequency')
            benchmark_value = request.form.get('benchmark_value')
            highlight_rule = request.form.get('highlight_rule')
            reminder = request.form.get('reminder')
            due_date_str = request.form.get('due_date')
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

            kpi = KPI(
                name=name,
                description=description,
                project_id=project.id,
                unit=unit,
                frequency=frequency,
                benchmark_value=float(benchmark_value),
                highlight_rule=highlight_rule,
                reminder=reminder,
                due_date=due_date
            )
            db.session.add(kpi)
            db.session.commit()
            flash('KPI created successfully!', 'success')
            return redirect(url_for('project.view_project', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating KPI: {str(e)}', 'error')

    kpis = KPI.query.filter_by(project_id=project.id).all()
    team_members = project.team_members

    # KPI summary stats
    total_kpis = len(kpis)
    achieved = sum(1 for k in kpis if k.status == 'completed')
    in_progress = sum(1 for k in kpis if k.status == 'pending')
    at_risk = sum(1 for k in kpis if k.status == 'at_risk')

    return render_template(
        'project/view.html',
        project=project,
        kpis=kpis,
        team_members=team_members,
        total_kpis=total_kpis,
        achieved=achieved,
        in_progress=in_progress,
        at_risk=at_risk
    )

@project_bp.route('/api/projects/<int:project_id>/kpis')
@login_required
def api_project_kpis(project_id):
    project = Project.query.get_or_404(project_id)
    if not (current_user.role == 'admin' or 
            current_user.id == project.project_manager_id or 
            current_user in project.team_members):
        return jsonify({'error': 'Unauthorized'}), 403
    kpis = KPI.query.filter_by(project_id=project.id).all()
    return jsonify([
        {
            'id': k.id,
            'name': k.name,
            'description': k.description,
            'target_value': k.target_value,
            'unit': k.unit,
            'frequency': k.frequency,
            'due_date': k.due_date.strftime('%Y-%m-%d'),
            'benchmark_type': k.benchmark_type,
            'benchmark_value': k.benchmark_value,
            'actual_value': k.actual_value,
            'status': k.status,
            'assigned_to': k.assigned_to.username if k.assigned_to else None
        }
        for k in kpis
    ])

@project_bp.route('/projects/<int:project_id>/update', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'project_manager')
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user has permission to update the project
    if not (current_user.role == 'admin' or current_user.id == project.project_manager_id):
        flash('You do not have permission to update this project.', 'error')
        return redirect(url_for('project.list_projects'))
    
    if request.method == 'POST':
        try:
            project.name = request.form.get('name')
            project.description = request.form.get('description')
            project.team_size = int(request.form.get('team_size'))
            project.monthly_cost = float(request.form.get('monthly_cost'))
            project.project_type = request.form.get('project_type')
            project.status = request.form.get('status')
            
            # Update team members
            team_member_ids = request.form.getlist('team_members')
            project.team_members = []
            if team_member_ids:
                team_members = User.query.filter(User.id.in_(team_member_ids)).all()
                project.team_members.extend(team_members)
            
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('project.view_project', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
    
    # Get all active users for resource allocation
    users = User.query.filter_by(status='active').all()
    return render_template('project/update.html', project=project, users=users)

@project_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'project_manager')
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'error')
    return redirect(url_for('project.list_projects')) 