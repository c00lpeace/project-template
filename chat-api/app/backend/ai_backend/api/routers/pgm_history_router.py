# _*_ coding: utf-8 _*_
"""PGM Mapping History REST API endpoints."""

import logging
from typing import Optional

from ai_backend.api.services.pgm_history_service import PgmHistoryService
from ai_backend.core.dependencies import get_pgm_history_service
from ai_backend.database.models.pgm_mapping_models import PgmMappingAction
from ai_backend.types.response.pgm_history_response import (
    MappingHistoryItemResponse,
    MappingHistoryResponse,
    MappingHistoryStatsResponse,
)
from fastapi import APIRouter, Depends, Query

logger = logging.getLogger(__name__)
router = APIRouter(tags=["pgm-history"])


@router.get("/pgm-history/plc/{plc_id}", response_model=MappingHistoryResponse)
def get_plc_mapping_history(
    plc_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(50, ge=1, le=100, description="조회할 개수"),
    history_service: PgmHistoryService = Depends(get_pgm_history_service)
):
    """특정 PLC의 매핑 변경 이력을 조회합니다."""
    histories, total = history_service.get_histories_by_plc(
        plc_id=plc_id,
        skip=skip,
        limit=limit
    )
    
    return MappingHistoryResponse(
        total=total,
        items=[MappingHistoryItemResponse.model_validate(h) for h in histories]
    )


@router.get("/pgm-history/program/{pgm_id}", response_model=MappingHistoryResponse)
def get_program_mapping_history(
    pgm_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(50, ge=1, le=100, description="조회할 개수"),
    history_service: PgmHistoryService = Depends(get_pgm_history_service)
):
    """특정 프로그램의 매핑 이력을 조회합니다."""
    histories, total = history_service.get_histories_by_program(
        pgm_id=pgm_id,
        skip=skip,
        limit=limit
    )
    
    return MappingHistoryResponse(
        total=total,
        items=[MappingHistoryItemResponse.model_validate(h) for h in histories]
    )


@router.get("/pgm-history/user/{action_user}", response_model=MappingHistoryResponse)
def get_user_mapping_history(
    action_user: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(50, ge=1, le=100, description="조회할 개수"),
    history_service: PgmHistoryService = Depends(get_pgm_history_service)
):
    """특정 사용자의 매핑 이력을 조회합니다."""
    histories, total = history_service.get_histories_by_user(
        action_user=action_user,
        skip=skip,
        limit=limit
    )
    
    return MappingHistoryResponse(
        total=total,
        items=[MappingHistoryItemResponse.model_validate(h) for h in histories]
    )


@router.get("/pgm-history/recent", response_model=MappingHistoryResponse)
def get_recent_mapping_history(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=200, description="조회할 개수"),
    action: Optional[str] = Query(None, description="액션 필터 (CREATE, UPDATE, DELETE, RESTORE)"),
    history_service: PgmHistoryService = Depends(get_pgm_history_service)
):
    """최근 매핑 변경 이력을 조회합니다."""
    action_enum = None
    if action:
        try:
            action_enum = PgmMappingAction(action)
        except ValueError:
            pass
    
    histories, total = history_service.get_recent_histories(
        skip=skip,
        limit=limit,
        action=action_enum
    )
    
    return MappingHistoryResponse(
        total=total,
        items=[MappingHistoryItemResponse.model_validate(h) for h in histories]
    )


@router.get("/pgm-history/plc/{plc_id}/stats", response_model=MappingHistoryStatsResponse)
def get_plc_history_stats(
    plc_id: str,
    history_service: PgmHistoryService = Depends(get_pgm_history_service)
):
    """특정 PLC의 매핑 이력 통계를 조회합니다."""
    stats = history_service.get_history_stats_by_plc(plc_id)
    return MappingHistoryStatsResponse(**stats)


@router.get("/pgm-history/{history_id}", response_model=MappingHistoryItemResponse)
def get_mapping_history(
    history_id: int,
    history_service: PgmHistoryService = Depends(get_pgm_history_service)
):
    """이력 ID로 특정 매핑 이력을 조회합니다."""
    history = history_service.get_history_by_id(history_id)
    return MappingHistoryItemResponse.model_validate(history)
