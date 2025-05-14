"""
Database seeding utility.
"""

import logging
from typing import List, Dict, Any
from app.core.database import db
from app.core.models.user import User
from app.core.models.role import Role
from app.core.models.permission import Permission, role_permissions

logger = logging.getLogger(__name__)

def seed_roles() -> List[Role]:
    """Seed default roles."""
    roles = [
        Role(name='admin', description='Administrator role'),
        Role(name='user', description='Regular user role'),
        Role(name='moderator', description='Moderator role')
    ]
    
    for role in roles:
        try:
            existing = Role.query.filter_by(name=role.name).first()
            if not existing:
                db.session.add(role)
        except Exception as e:
            logger.error(f"Failed to seed role {role.name}: {str(e)}")
            raise
    
    db.session.commit()
    return roles

def seed_users() -> List[User]:
    """Seed default users."""
    users = [
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'username': 'user',
            'email': 'user@example.com',
            'password': 'user123',
            'role': 'user'
        }
    ]
    
    created_users = []
    for user_data in users:
        try:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                role = Role.query.filter_by(name=user_data['role']).first()
                if not role:
                    logger.error(f"Role {user_data['role']} not found")
                    continue
                
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=role
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                created_users.append(user)
        except Exception as e:
            logger.error(f"Failed to seed user {user_data['username']}: {str(e)}")
            raise
    
    db.session.commit()
    return created_users

def seed_permissions() -> list:
    """Seed default permissions."""
    permissions = [
        Permission(name='view_dashboard', description='View dashboard'),
        Permission(name='manage_users', description='Manage users'),
        Permission(name='edit_content', description='Edit content'),
        Permission(name='delete_content', description='Delete content'),
    ]
    for perm in permissions:
        try:
            existing = Permission.query.filter_by(name=perm.name).first()
            if not existing:
                db.session.add(perm)
        except Exception as e:
            logger.error(f"Failed to seed permission {perm.name}: {str(e)}")
            raise
    db.session.commit()
    return permissions

def seed_roles_and_permissions():
    """Seed roles and assign permissions."""
    roles = seed_roles()
    permissions = seed_permissions()
    # Assign all permissions to admin, limited to others
    admin_role = Role.query.filter_by(name='admin').first()
    user_role = Role.query.filter_by(name='user').first()
    moderator_role = Role.query.filter_by(name='moderator').first()
    if admin_role:
        admin_role.permissions = permissions
    if user_role:
        user_role.permissions = [p for p in permissions if p.name == 'view_dashboard']
    if moderator_role:
        moderator_role.permissions = [p for p in permissions if p.name in ['view_dashboard', 'edit_content']]
    db.session.commit()

def seed_database():
    """Seed the database with initial data."""
    try:
        logger.info("Starting database seeding...")
        
        # Seed roles first
        roles = seed_roles()
        logger.info(f"Seeded {len(roles)} roles")
        
        # Seed users
        users = seed_users()
        logger.info(f"Seeded {len(users)} users")
        
        # Seed permissions and assign them to roles
        seed_roles_and_permissions()
        logger.info("Roles and permissions seeded successfully")
        
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Database seeding failed: {str(e)}")
        db.session.rollback()
        raise 