"""Models for auth_user system"""

# Auto-generated imports
from .auth_relationship_models import *
from .models import *
from .user_models import *

# Explicit exports for commonly needed items
from .user_models import Permission, role_permissions_table

# Provide an alias for role_permissions
role_permissions = role_permissions_table
