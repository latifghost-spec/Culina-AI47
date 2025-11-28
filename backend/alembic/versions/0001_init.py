from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
    )
    op.create_table('suppliers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('lead_time_days', sa.Integer(), nullable=True),
    )
    op.create_table('supplier_products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('supplier_name', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('grade', sa.String(), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=True),
        sa.Column('lead_time_days', sa.Integer(), nullable=True),
        sa.Column('sustainability', sa.Float(), nullable=True),
    )
    op.create_table('inventory_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('stock_qty', sa.Float(), nullable=True),
        sa.Column('reorder_point', sa.Float(), nullable=True),
        sa.Column('reserve_qty', sa.Float(), nullable=True),
        sa.Column('unit_price_per_kg', sa.Float(), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
    )

def downgrade():
    op.drop_table('inventory_items')
    op.drop_table('supplier_products')
    op.drop_table('suppliers')
    op.drop_table('users')
