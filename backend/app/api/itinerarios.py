"""POST /itinerarios, GET /itinerarios/me, GET /itinerarios/{id} y
DELETE /itinerarios/{id}. Todas protegidas: un itinerario siempre
pertenece a una cuenta (no tiene sentido guardarlo de forma anónima, ya
que "Mis Itinerarios" es, justamente, para volver a verlo después).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_usuario_actual
from app.database.conexion import get_db
from app.models.usuarios import Usuario
from app.schemas.itinerarios import (
    ItinerarioEntrada,
    ItinerarioPublico,
    ItinerarioRenombrarEntrada,
    ItinerarioResumen,
    ParadaActualizarEntrada,
    ParadaEntrada,
    ParadaPublica,
    ReordenarParadasEntrada,
)
from app.services import itinerarios_service

router = APIRouter(prefix="/itinerarios", tags=["Itinerarios"])


@router.post("", response_model=ItinerarioPublico, status_code=status.HTTP_201_CREATED)
def crear_itinerario(
    datos: ItinerarioEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    try:
        return itinerarios_service.crear_itinerario(db, usuario.id, datos)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/me", response_model=list[ItinerarioResumen])
def listar_mis_itinerarios(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    return itinerarios_service.listar_mios(db, usuario.id)


@router.get("/{itinerario_id}", response_model=ItinerarioPublico)
def ver_itinerario(
    itinerario_id: int,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    return itinerario


@router.patch("/{itinerario_id}", response_model=ItinerarioPublico)
def renombrar_itinerario(
    itinerario_id: int,
    datos: ItinerarioRenombrarEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    return itinerarios_service.renombrar(db, itinerario, datos.titulo)


@router.delete("/{itinerario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_itinerario(
    itinerario_id: int,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    itinerarios_service.eliminar(db, itinerario)


@router.post("/{itinerario_id}/paradas", response_model=ParadaPublica, status_code=status.HTTP_201_CREATED)
def agregar_parada(
    itinerario_id: int,
    datos: ParadaEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    try:
        return itinerarios_service.agregar_parada(db, itinerario, datos)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.delete("/{itinerario_id}/paradas/{parada_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_parada(
    itinerario_id: int,
    parada_id: int,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    try:
        itinerarios_service.eliminar_parada(db, itinerario, parada_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.patch("/{itinerario_id}/paradas/{parada_id}", response_model=ParadaPublica)
def actualizar_parada(
    itinerario_id: int,
    parada_id: int,
    datos: ParadaActualizarEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    try:
        return itinerarios_service.marcar_parada_visitada(db, itinerario, parada_id, datos.visitado)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.put("/{itinerario_id}/paradas/reordenar", response_model=ItinerarioPublico)
def reordenar_paradas(
    itinerario_id: int,
    datos: ReordenarParadasEntrada,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    itinerario = itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
    if itinerario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerario no encontrado")
    try:
        itinerarios_service.reordenar_paradas(db, itinerario, datos.dia_numero, datos.orden_ids)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    db.refresh(itinerario)
    return itinerarios_service.obtener_por_id(db, itinerario_id, usuario.id)
