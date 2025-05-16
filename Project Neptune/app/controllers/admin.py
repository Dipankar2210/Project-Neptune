from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app import db
from app.controllers.auth import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/users')
@login_required
@role_required('admin')
def manage_users():
    pending_users = User.query.filter_by(status='pending').all()
    active_users = User.query.filter_by(status='active').all()
    return render_template('admin/users.html', pending_users=pending_users, active_users=active_users)

@admin_bp.route('/admin/assign_role/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def assign_role(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form.get('role')
    
    if role not in ['admin', 'project_manager', 'project_head', 'team_member']:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    user.role = role
    user.activate()
    db.session.commit()
    
    flash(f'Role {role} assigned to {user.username} successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('new_role')
    
    if new_role not in ['admin', 'project_manager', 'project_head', 'team_member']:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'Role changed to {new_role} for {user.username} successfully.', 'success')
    return redirect(url_for('admin.manage_users')) 