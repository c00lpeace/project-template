# _*_ coding: utf-8 _*_
"""PGM Mapping History response models."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

__all__ = [
    "MappingHistoryItemResponse",
    "MappingHistoryResponse",
    "MappingHistoryStatsResponse",
]


class MappingHistoryItemResponse(BaseModel):
    """매핑 이력 항목 응답"""
    history_id: int
    plc_id: str
    pgm_id: Optional[str]
    action: str = Field(..., description="CREATE, UPDATE, DELETE, RESTORE")
    action_dt: datetime
    action_user: Optional[str]
    prev_pgm_id: Optional[str] = Field(None, description="이전 프로그램 ID")
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class MappingHistoryResponse(BaseModel):
    """매핑 이력 목록 응답"""
    items: List[MappingHistoryItemResponse]
    total: int = Field(..., description="전체 이력 개수")


class MappingHistoryStatsResponse(BaseModel):
    """매핑 이력 통계 응답"""
    plc_id: str
    total_changes: int = Field(..., description="총 변경 횟수")
    create_count: int = Field(..., description="생성 횟수")
    update_count: int = Field(..., description="수정 횟수")
    delete_count: int = Field(..., description="삭제 횟수")
    restore_count: int = Field(..., description="복원 횟수")
    latest_action: Optional[MappingHistoryItemResponse] = Field(None, description="최근 변경")
