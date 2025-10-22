# _*_ coding: utf-8 _*_
"""Program REST API endpoints."""

from fastapi import APIRouter, Depends, Query
from ai_backend.core.dependencies import get_program_service, get_plc_service
from ai_backend.api.services.program_service import ProgramService
from ai_backend.api.services.plc_service import PlcService
from ai_backend.types.request.program_request import (
    CreateProgramRequest,
    UpdateProgramRequest,
)
from ai_backend.types.response.program_response import (
    ProgramResponse,
    ProgramListResponse,
    ProgramDeleteResponse,
)
from ai_backend.types.response.plc_response import (
    PlcsByProgramResponse,
    PlcWithMappingResponse,
)
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["programs"])


@router.post("/programs", response_model=ProgramResponse)
def create_program(
    request: CreateProgramRequest,
    program_service: ProgramService = Depends(get_program_service)
):
    """프로그램을 생성"""
    program = program_service.create_program(
        pgm_id=request.pgm_id,
        pgm_name=request.pgm_name,
        ladder_doc_id=request.ladder_doc_id,
        template_doc_id=request.template_doc_id,
        pgm_version=request.pgm_version,
        description=request.description,
        create_user=request.create_user,
        notes=request.notes
    )
    return ProgramResponse.from_orm(program)


@router.get("/programs/{pgm_id}", response_model=ProgramResponse)
def get_program(
    pgm_id: str,
    program_service: ProgramService = Depends(get_program_service)
):
    """프로그램을 조회 (PGM_ID)"""
    program = program_service.get_program(pgm_id)
    return ProgramResponse.from_orm(program)


@router.get("/programs", response_model=ProgramListResponse)
def get_programs(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(50, ge=1, le=100, description="페이지당 개수"),
    search: Optional[str] = Query(None, description="검색어 (ID 또는 명칭)"),
    pgm_version: Optional[str] = Query(None, description="프로그램 버전 필터"),
    program_service: ProgramService = Depends(get_program_service)
):
    """프로그램 목록을 조회"""
    skip = (page - 1) * page_size
    programs, total_count = program_service.get_programs(
        skip=skip,
        limit=page_size,
        search=search,
        pgm_version=pgm_version
    )
    
    return ProgramListResponse(
        items=[ProgramResponse.from_orm(p) for p in programs],
        total_count=total_count,
        page=page,
        page_size=page_size
    )


@router.put("/programs/{pgm_id}", response_model=ProgramResponse)
def update_program(
    pgm_id: str,
    request: UpdateProgramRequest,
    program_service: ProgramService = Depends(get_program_service)
):
    """프로그램을 수정"""
    program = program_service.update_program(
        pgm_id=pgm_id,
        pgm_name=request.pgm_name,
        ladder_doc_id=request.ladder_doc_id,
        template_doc_id=request.template_doc_id,
        pgm_version=request.pgm_version,
        description=request.description,
        notes=request.notes,
        update_user=request.update_user
    )
    return ProgramResponse.from_orm(program)


@router.delete("/programs/{pgm_id}", response_model=ProgramDeleteResponse)
def delete_program(
    pgm_id: str,
    program_service: ProgramService = Depends(get_program_service)
):
    """프로그램을 삭제"""
    program_service.delete_program(pgm_id)
    
    return ProgramDeleteResponse(
        pgm_id=pgm_id,
        message="프로그램이 성공적으로 삭제되었습니다."
    )


# ========== 프로그램별 매핑 PLC 조회 API ==========

@router.get("/programs/{pgm_id}/plcs", response_model=PlcsByProgramResponse)
def get_plcs_by_program(
    pgm_id: str,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=100, description="조회할 개수"),
    plc_service: PlcService = Depends(get_plc_service)
):
    """
    특정 프로그램에 매핑된 PLC 목록을 조회
    
    해당 프로그램을 사용하는 모든 PLC를 조회
    """
    plcs, total_count = plc_service.get_plcs_by_program(
        pgm_id=pgm_id,
        skip=skip,
        limit=limit
    )
    
    return PlcsByProgramResponse(
        pgm_id=pgm_id,
        total_count=total_count,
        items=[PlcWithMappingResponse.from_orm(plc) for plc in plcs]
    )
