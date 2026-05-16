from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.emergency import (
    EmergencyAdmissionRequest,
    CaseResponse,
    CaseListResponse,
)
from app.schemas.base import SuccessResponse, ErrorResponse
from app.services.emergency_service import EmergencyService
from app.utils.logger import get_logger
from app.utils.exceptions import EmergenciaSyncException

logger = get_logger("api.routes.emergency")

router = APIRouter(
    prefix="/api/v1/emergencies",
    tags=["Emergencies"],
)


@router.post(
    "/admission",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Webhook de admisión a emergencia",
    description="""
    Webhook que se activa cuando un paciente ingresa a emergencia.
    
    Valida póliza, pre-existencias y emite decisión instantánea.
    
    """,
)
async def admission_webhook(
    request: EmergencyAdmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Procesa ingreso a emergencia.

    Pasos:
    1. Valida datos de entrada
    2. Ejecuta agente IA
    3. Crea registro de caso
    4. Retorna decisión

    Args:
        request: Datos del ingreso
        db: Session de BD

    Returns:
        Decisión del agente

    Raises:
        HTTPException: Si hay error en validación
    """
    try:
        logger.info(f"Webhook recibido para cédula: {request.cedula}")

        service = EmergencyService(db)
        result = service.process_emergency_admission(request)

        logger.info(f"Admisión procesada. Case ID: {result['case_id']}")

        return SuccessResponse(
            success=True,
            message="Emergencia procesada exitosamente",
            data=result,
        )

    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except EmergenciaSyncException as e:
        logger.error(f"Error de aplicación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error no controlado: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get(
    "/cases",
    response_model=SuccessResponse,
    summary="Listar casos recientes",
    description="Obtiene últimos casos de emergencia procesados",
)
async def list_cases(
    limit: int = 20,
    hours: int = 24,
    db: Session = Depends(get_db),
):
    """
    Lista casos recientes.

    Args:
        limit: Límite de resultados (max 100)
        hours: Últimas N horas (default 24)
        db: Session de BD

    Returns:
        Lista de casos
    """
    try:
        # Validar parámetros
        if limit > 100:
            limit = 100
        if hours < 1:
            hours = 1

        service = EmergencyService(db)
        result = service.get_recent_cases(limit=limit, hours=hours)

        logger.info(f"Listando {len(result['cases'])} casos recientes")

        return SuccessResponse(
            success=True,
            message=f"Se encontraron {result['total']} casos",
            data=result,
        )

    except Exception as e:
        logger.error(f"Error listando casos: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener casos",
        )


@router.get(
    "/cases/{case_id}",
    response_model=SuccessResponse,
    summary="Detalle de caso",
    description="Obtiene información detallada de un caso específico",
)
async def get_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    """
    Obtiene detalle de un caso.

    Args:
        case_id: ID del caso
        db: Session de BD

    Returns:
        Detalles del caso

    Raises:
        HTTPException: Si caso no existe
    """
    try:
        service = EmergencyService(db)
        case = service.get_case_details(case_id)

        if not case:
            logger.warning(f"Caso no encontrado: {case_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Caso {case_id} no encontrado",
            )

        logger.info(f"Obteniendo detalles del caso: {case_id}")

        return SuccessResponse(
            success=True,
            message="Caso obtenido exitosamente",
            data=case,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error obteniendo caso: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener caso",
        )


@router.get(
    "/statistics",
    response_model=SuccessResponse,
    summary="Estadísticas de casos",
    description="Obtiene estadísticas de casos procesados en el período",
)
async def get_statistics(
    hours: int = 24,
    db: Session = Depends(get_db),
):
    """
    Obtiene estadísticas.

    Args:
        hours: Período en horas
        db: Session de BD

    Returns:
        Estadísticas
    """
    try:
        if hours < 1:
            hours = 1

        service = EmergencyService(db)
        stats = service.get_statistics(hours=hours)

        logger.info(f"Estadísticas de últimas {hours} horas")

        return SuccessResponse(
            success=True,
            message="Estadísticas obtenidas",
            data=stats,
        )

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas",
        )
