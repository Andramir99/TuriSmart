"""agrega campos de catalogo enriquecido a lugares

Revision ID: a1f3c8e92d4b
Revises: b29a8f6a163f
Create Date: 2026-10-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1f3c8e92d4b'
down_revision: Union[str, Sequence[str], None] = 'b29a8f6a163f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('lugares', sa.Column('descripcion_corta', sa.String(length=200), nullable=True))
    op.add_column('lugares', sa.Column('tipo_turismo', sa.String(length=120), nullable=True))
    op.add_column(
        'lugares',
        sa.Column('nivel_popularidad', sa.Integer(), nullable=False, server_default='1'),
    )
    op.add_column(
        'lugares',
        sa.Column('servicios_disponibles', sa.ARRAY(sa.String(length=60)), nullable=True),
    )
    op.add_column('lugares', sa.Column('recomendaciones_visitante', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('lugares', 'recomendaciones_visitante')
    op.drop_column('lugares', 'servicios_disponibles')
    op.drop_column('lugares', 'nivel_popularidad')
    op.drop_column('lugares', 'tipo_turismo')
    op.drop_column('lugares', 'descripcion_corta')
