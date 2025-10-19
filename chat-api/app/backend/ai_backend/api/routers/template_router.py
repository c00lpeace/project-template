# _*_ coding: utf-8 _*_
"""Template Management API endpoints"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
import logging

from ai_backend.core.dependencies import get_template_service
from ai_backend.api.services.template_service import TemplateService
from ai_backend.types.response.template_response import (
    TemplateTreeResponse,
    TemplateListResponse,
    TemplateStatsResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["template-management"])


@router.get("/templates/{pgm_id}", response_model=TemplateTreeResponse)
def get_template_tree(
    pgm_id: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """프로그램별 템플릿 트리 구조 조회
    
    Args:
        pgm_id: 프로그램 ID
        
    Returns:
        TemplateTreeResponse: 폴더/서브폴더/로직 계층 구조
    """
    result = template_service.get_template_tree(pgm_id)
    return result


@router.get("/templates", response_model=TemplateListResponse)
def get_template_list(
    pgm_id: Optional[str] = Query(None, description="프로그램 ID 필터"),
    folder_id: Optional[str] = Query(None, description="폴더 ID 필터"),
    logic_name: Optional[str] = Query(None, description="로직명 검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(100, ge=1, le=1000, description="페이지 크기"),
    template_service: TemplateService = Depends(get_template_service)
):
    """템플릿 목록 조회 (검색, 페이징)
    
    Args:
        pgm_id: 프로그램 ID (선택)
        folder_id: 폴더 ID (선택)
        logic_name: 로직명 검색어 (선택)
        page: 페이지 번호
        page_size: 페이지 크기
        
    Returns:
        TemplateListResponse: 템플릿 목록
    """
    result = template_service.get_template_list(
        pgm_id=pgm_id,
        folder_id=folder_id,
        logic_name=logic_name,
        page=page,
        page_size=page_size
    )
    return result


@router.delete("/templates/{pgm_id}")
def delete_template(
    pgm_id: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """프로그램별 템플릿 삭제
    
    Args:
        pgm_id: 프로그램 ID
        
    Returns:
        삭제 결과
    """
    result = template_service.delete_template(pgm_id)
    return {
        "status": "success",
        "message": f"프로그램 {pgm_id}의 템플릿이 삭제되었습니다.",
        "data": result
    }


@router.get("/templates-summary", response_model=TemplateStatsResponse)
def get_template_stats(
    template_service: TemplateService = Depends(get_template_service)
):
    """모든 프로그램의 템플릿 요약 정보 조회
    
    Returns:
        TemplateStatsResponse: 템플릿 통계
    """
    summaries = template_service.get_all_template_summary()
    
    total_templates = sum(s.template_count for s in summaries)
    
    return TemplateStatsResponse(
        total_programs=len(summaries),
        total_templates=total_templates,
        programs=summaries
    )


@router.get("/templates/count/{pgm_id}")
def get_template_count(
    pgm_id: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """프로그램별 템플릿 개수 조회
    
    Args:
        pgm_id: 프로그램 ID
        
    Returns:
        템플릿 개수
    """
    from ai_backend.database.crud.template_crud import TemplateCrud
    count = TemplateCrud.get_template_count_by_pgm(template_service.db, pgm_id)
    
    return {
        "status": "success",
        "data": {
            "pgm_id": pgm_id,
            "template_count": count
        }
    }
