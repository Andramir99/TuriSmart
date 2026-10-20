"""agrega visitado a detalle_itinerario

Revision ID: b29a8f6a163f
Revises: 15c9b4d1d031
Create Date: 2026-09-16 20:49:29.101351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b29a8f6a163f'
down_revision: Union[str, Sequence[str], None] = '15c9b4d1d031'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTA: no se llama a op.drop_table('spatial_ref_sys'). Alembic la
    # detecta como "tabla removida" porque la crea PostGIS, no nuestros
    # modelos — no es nuestra, nunca se debe borrar (ver lugares.py).
    op.add_column(
        'detalle_itinerario',
        sa.Column('visitado', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('detalle_itinerario', 'visitado')
