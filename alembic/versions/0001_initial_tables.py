"""Create initial 11 tables for hospital operations platform

Revision ID: 0001_initial_tables
Revises: 
Create Date: 2026-11-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. hospitals
    op.create_table(
        'hospitals',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_hospitals_code', 'hospitals', ['code'], unique=True)
    op.create_index('ix_hospitals_city', 'hospitals', ['city'], unique=False)

    # 2. roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, unique=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)

    # 3. permissions
    op.create_table(
        'permissions',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False, unique=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_permissions_code', 'permissions', ['code'], unique=True)
    op.create_index('ix_permissions_category', 'permissions', ['category'], unique=False)

    # 4. role_permissions
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('role_id', sa.Uuid(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission_id', sa.Uuid(as_uuid=True), sa.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('constraints', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    op.create_index('ix_role_permissions_role_id', 'role_permissions', ['role_id'])
    op.create_index('ix_role_permissions_permission_id', 'role_permissions', ['permission_id'])

    # 5. users
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False, unique=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_hospital_id', 'users', ['hospital_id'])
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 6. user_roles
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', sa.Uuid(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    op.create_index('ix_user_roles_hospital_id', 'user_roles', ['hospital_id'])
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])
    op.create_index('idx_user_roles_tenant_user', 'user_roles', ['hospital_id', 'user_id'])

    # 7. user_permission_overrides
    op.create_table(
        'user_permission_overrides',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('permission_id', sa.Uuid(as_uuid=True), sa.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_granted', sa.Boolean(), nullable=False),
        sa.Column('constraints_override', sa.JSON(), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_by_user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'permission_id', name='uq_user_permission_override'),
    )
    op.create_index('ix_user_permission_overrides_hospital_id', 'user_permission_overrides', ['hospital_id'])
    op.create_index('ix_user_permission_overrides_user_id', 'user_permission_overrides', ['user_id'])
    op.create_index('ix_user_permission_overrides_permission_id', 'user_permission_overrides', ['permission_id'])
    op.create_index('idx_override_tenant_user', 'user_permission_overrides', ['hospital_id', 'user_id'])

    # 8. inventory_items
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('batch_number', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reorder_level', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('quantity >= 0', name='chk_inventory_quantity_non_negative'),
        sa.CheckConstraint('unit_price >= 0', name='chk_inventory_unit_price_non_negative'),
    )
    op.create_index('ix_inventory_items_hospital_id', 'inventory_items', ['hospital_id'])
    op.create_index('ix_inventory_items_sku', 'inventory_items', ['sku'])
    op.create_index('ix_inventory_items_name', 'inventory_items', ['name'])
    op.create_index('ix_inventory_items_category', 'inventory_items', ['category'])
    op.create_index('ix_inventory_items_batch_number', 'inventory_items', ['batch_number'])
    op.create_index('ix_inventory_items_expiry_date', 'inventory_items', ['expiry_date'])
    op.create_index('idx_inventory_tenant_sku', 'inventory_items', ['hospital_id', 'sku'])
    op.create_index('idx_inventory_tenant_category', 'inventory_items', ['hospital_id', 'category'])
    op.create_index('idx_inventory_tenant_expiry', 'inventory_items', ['hospital_id', 'expiry_date'])
    op.create_index('idx_inventory_tenant_quantity', 'inventory_items', ['hospital_id', 'quantity'])

    # 9. bills
    op.create_table(
        'bills',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('bill_number', sa.String(length=100), nullable=False),
        sa.Column('patient_name', sa.String(length=255), nullable=False),
        sa.Column('patient_mrn', sa.String(length=100), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('discount_pct', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('final_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('doctor_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_by_user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('bill_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('total_amount >= 0', name='chk_bills_total_non_negative'),
        sa.CheckConstraint('discount_pct >= 0 AND discount_pct <= 100', name='chk_bills_discount_range'),
        sa.CheckConstraint('final_amount >= 0', name='chk_bills_final_non_negative'),
    )
    op.create_index('ix_bills_hospital_id', 'bills', ['hospital_id'])
    op.create_index('ix_bills_bill_number', 'bills', ['bill_number'])
    op.create_index('ix_bills_patient_name', 'bills', ['patient_name'])
    op.create_index('ix_bills_patient_mrn', 'bills', ['patient_mrn'])
    op.create_index('ix_bills_status', 'bills', ['status'])
    op.create_index('ix_bills_doctor_id', 'bills', ['doctor_id'])
    op.create_index('ix_bills_created_by_user_id', 'bills', ['created_by_user_id'])
    op.create_index('ix_bills_bill_date', 'bills', ['bill_date'])
    op.create_index('idx_bills_tenant_number', 'bills', ['hospital_id', 'bill_number'])
    op.create_index('idx_bills_tenant_status', 'bills', ['hospital_id', 'status'])
    op.create_index('idx_bills_tenant_date', 'bills', ['hospital_id', 'bill_date'])
    op.create_index('idx_bills_tenant_mrn', 'bills', ['hospital_id', 'patient_mrn'])
    op.create_index('idx_bills_tenant_creator', 'bills', ['hospital_id', 'created_by_user_id'])

    # 10. pending_operations
    op.create_table(
        'pending_operations',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('target_resource', sa.String(length=100), nullable=False),
        sa.Column('filter_criteria', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('proposed_changes', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('impacted_row_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('preview_diff', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmed_by_user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_pending_operations_hospital_id', 'pending_operations', ['hospital_id'])
    op.create_index('ix_pending_operations_user_id', 'pending_operations', ['user_id'])
    op.create_index('ix_pending_operations_operation_type', 'pending_operations', ['operation_type'])
    op.create_index('ix_pending_operations_target_resource', 'pending_operations', ['target_resource'])
    op.create_index('ix_pending_operations_status', 'pending_operations', ['status'])
    op.create_index('ix_pending_operations_expires_at', 'pending_operations', ['expires_at'])
    op.create_index('ix_pending_operations_created_at', 'pending_operations', ['created_at'])
    op.create_index('idx_pending_tenant_status', 'pending_operations', ['hospital_id', 'status'])
    op.create_index('idx_pending_tenant_expiry', 'pending_operations', ['hospital_id', 'expires_at'])

    # 11. audit_log
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('hospital_id', sa.Uuid(as_uuid=True), sa.ForeignKey('hospitals.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.Column('metadata_info', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_audit_log_hospital_id', 'audit_log', ['hospital_id'])
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_resource_type', 'audit_log', ['resource_type'])
    op.create_index('ix_audit_log_status', 'audit_log', ['status'])
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])
    op.create_index('idx_audit_tenant_action', 'audit_log', ['hospital_id', 'action'])
    op.create_index('idx_audit_tenant_resource', 'audit_log', ['hospital_id', 'resource_type'])
    op.create_index('idx_audit_tenant_created', 'audit_log', ['hospital_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('pending_operations')
    op.drop_table('bills')
    op.drop_table('inventory_items')
    op.drop_table('user_permission_overrides')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('hospitals')
