"""seudonimiza usuario_id en encuestas

Revision ID: 49d935f3cf27
Revises: 0c6a2eb08ded
Create Date: 2026-09-16 19:34:52.179403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.anonimizacion import seudonimizar_usuario_id


# revision identifiers, used by Alembic.
revision: str = '49d935f3cf27'
down_revision: Union[str, Sequence[str], None] = '0c6a2eb08ded'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('encuestas', sa.Column('usuario_id_seudonimo', sa.String(length=16), nullable=True))

    # Backfill: las filas que ya tenian usuario_id real quedan con su
    # seudonimo correspondiente, en vez de perder ese dato de golpe.
    conexion = op.get_bind()
    filas = conexion.execute(
        sa.text('SELECT id, usuario_id FROM encuestas WHERE usuario_id IS NOT NULL')
    ).fetchall()
    for fila in filas:
        conexion.execute(
            sa.text('UPDATE encuestas SET usuario_id_seudonimo = :seudonimo WHERE id = :id'),
            {'seudonimo': seudonimizar_usuario_id(fila.usuario_id), 'id': fila.id},
        )

    op.drop_column('encuestas', 'usuario_id')


def downgrade() -> None:
    """Downgrade schema."""
    # No es posible revertir un seudonimo (hash de un solo sentido) a su
    # usuario_id real - la columna vuelve a crearse vacia.
    op.add_column('encuestas', sa.Column('usuario_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'encuestas_usuario_id_fkey', 'encuestas', 'usuarios', ['usuario_id'], ['id'], ondelete='SET NULL'
    )
    op.drop_column('encuestas', 'usuario_id_seudonimo')
