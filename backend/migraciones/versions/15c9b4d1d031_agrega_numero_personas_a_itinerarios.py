"""agrega numero_personas a itinerarios

Revision ID: 15c9b4d1d031
Revises: e47c9734a2bc
Create Date: 2026-09-16 20:33:00.356508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15c9b4d1d031'
down_revision: Union[str, Sequence[str], None] = 'e47c9734a2bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTA: no se llama a op.drop_table('spatial_ref_sys'). Alembic la
    # detecta como "tabla removida" porque la crea PostGIS, no nuestros
    # modelos — no es nuestra, nunca se debe borrar (ver lugares.py).
    op.add_column(
        'itinerarios',
        sa.Column('numero_personas', sa.Integer(), nullable=False, server_default='1'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('itinerarios', 'numero_personas')
