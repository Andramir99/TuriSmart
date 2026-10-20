"""agrega medio_transporte a preferencias

Revision ID: 0c6a2eb08ded
Revises: 5b5952f6dd9d
Create Date: 2026-09-02 23:31:24.212617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c6a2eb08ded'
down_revision: Union[str, Sequence[str], None] = '5b5952f6dd9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTA: no se llama a op.drop_table('spatial_ref_sys'). Alembic la
    # detecta como "tabla removida" porque la crea PostGIS, no nuestros
    # modelos — no es nuestra, nunca se debe borrar (ver lugares.py).
    op.add_column(
        'preferencias',
        sa.Column(
            'medio_transporte', sa.String(length=20), nullable=False, server_default='cualquiera'
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('preferencias', 'medio_transporte')
