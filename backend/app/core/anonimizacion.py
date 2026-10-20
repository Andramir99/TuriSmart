"""Seudonimización del usuario que responde una encuesta.

La tabla "encuestas" existe únicamente con fines de investigación
(entrenar y analizar el modelo de recomendación, Etapa 13): ninguna
pantalla de la aplicación le muestra al usuario su propio historial de
encuestas, así que no hay ninguna razón funcional para guardar ahí su
usuario_id real, que permitiría (con un JOIN a "usuarios") identificarlo
directamente por nombre y correo.

En su lugar se guarda un hash de un solo sentido: el mismo usuario_id
siempre produce el mismo seudónimo (para poder agrupar su patrón de
comportamiento en el análisis), pero no se puede revertir al usuario_id
real solo con los datos de esta tabla.
"""

import hashlib

# No es un secreto de seguridad (el usuario_id no es información sensible
# por sí solo) — es solo una sal fija para que el mismo usuario_id
# siempre produzca el mismo hash. Mismo valor usado en
# scripts/04_preparar_dataset.py, para mantener consistencia entre lo que
# guarda la aplicación y lo que consume el pipeline de entrenamiento.
SAL_ANONIMIZACION = "turismart-lima-tesis-2026"


def seudonimizar_usuario_id(usuario_id: int | None) -> str | None:
    if usuario_id is None:
        return None
    texto = f"{SAL_ANONIMIZACION}:{usuario_id}"
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]
