from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.project import Project

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
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
    
    return render_template('main/index.html', projects=projects) 