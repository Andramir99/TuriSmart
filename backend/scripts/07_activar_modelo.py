"""Etapa 15 — "Promueve" un modelo ya entrenado (scripts/06) a activo,
para que el backend empiece a usarlo de verdad en POST /recomendaciones/ml.

Nunca hay dos modelos del mismo tipo activos a la vez: activar uno
desactiva automáticamente cualquier otro del mismo "tipo" (por ahora,
"knn") que estuviera activo antes.

Ejecutar desde backend/, con el entorno virtual activado:
    python scripts/07_activar_modelo.py --listar
    python scripts/07_activar_modelo.py <id_del_modelo>
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.conexion import SessionLocal  # noqa: E402
from app.models.modelos_ml import ModeloML  # noqa: E402


def listar(db) -> None:
    modelos = db.query(ModeloML).order_by(ModeloML.fecha_creacion.desc()).all()
    if not modelos:
        print("Todavía no hay ningún modelo registrado. Corre primero scripts/06_entrenar_modelo.py.")
        return

    print(f"{'id':<4} {'tipo':<8} {'version':<8} {'activo':<7} {'métricas (KNN)'}")
    for modelo in modelos:
        metricas_knn = (modelo.metricas or {}).get("knn_contenido", {})
        resumen = (
            f"P@{metricas_knn.get('k', '?')}={metricas_knn.get('precision_at_k', '-')} "
            f"R@{metricas_knn.get('k', '?')}={metricas_knn.get('recall_at_k', '-')} "
            f"NDCG@{metricas_knn.get('k', '?')}={metricas_knn.get('ndcg_at_k', '-')}"
            if metricas_knn
            else "-"
        )
        print(f"{modelo.id:<4} {modelo.tipo:<8} {modelo.version:<8} {str(modelo.activo):<7} {resumen}")


def activar(db, modelo_id: int) -> None:
    modelo = db.query(ModeloML).filter(ModeloML.id == modelo_id).first()
    if modelo is None:
        print(f"No existe un modelo con id={modelo_id}.")
        return

    if not os.path.exists(modelo.ruta_archivo or ""):
        print(f"⚠️  El archivo {modelo.ruta_archivo} no existe en disco. No se activó nada.")
        return

    db.query(ModeloML).filter(ModeloML.tipo == modelo.tipo, ModeloML.activo.is_(True)).update(
        {"activo": False}
    )
    modelo.activo = True
    db.commit()
    print(f"Modelo id={modelo.id} ({modelo.nombre}, v{modelo.version}) activado.")
    print("POST /recomendaciones/ml ahora usa este modelo.")


def main():
    db = SessionLocal()
    try:
        if "--listar" in sys.argv or len(sys.argv) == 1:
            listar(db)
            return
        activar(db, int(sys.argv[1]))
    finally:
        db.close()


if __name__ == "__main__":
    main()
