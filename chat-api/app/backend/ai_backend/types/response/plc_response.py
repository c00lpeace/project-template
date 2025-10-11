# _*_ coding: utf-8 _*_
"""PLC response models."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class PlcResponse(BaseModel):
    """PLC 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    plc_id: str = Field(..., description="PLC ID")
    plant: str = Field(..., description="Plant")
    process: str = Field(..., description="공정")
    line: str = Field(..., description="Line")
    equipment_group: str = Field(..., description="장비그룹")
    unit: str = Field(..., description="호기")
    plc_name: str = Field(..., description="PLC 명칭")
    is_active: bool = Field(..., description="활성 상태")
    create_dt: datetime = Field(..., description="생성일시")
    update_dt: Optional[datetime] = Field(None, description="수정일시")


class PlcCreateResponse(BaseModel):
    """PLC 생성 응답"""
    plc_id: str = Field(..., description="PLC ID")
    plant: str = Field(..., description="Plant")
    process: str = Field(..., description="공정")
    line: str = Field(..., description="Line")
    equipment_group: str = Field(..., description="장비그룹")
    unit: str = Field(..., description="호기")
    plc_name: str = Field(..., description="PLC 명칭")


class PlcUpdateResponse(BaseModel):
    """PLC 수정 응답"""
    plc_id: str = Field(..., description="PLC ID")
    plant: str = Field(..., description="Plant")
    process: str = Field(..., description="공정")
    line: str = Field(..., description="Line")
    equipment_group: str = Field(..., description="장비그룹")
    unit: str = Field(..., description="호기")
    plc_name: str = Field(..., description="PLC 명칭")
    update_dt: Optional[datetime] = Field(None, description="수정일시")


class PlcDeleteResponse(BaseModel):
    """PLC 삭제 응답"""
    plc_id: str = Field(..., description="삭제된 PLC ID")
    message: str = Field(..., description="메시지")


class PlcRestoreResponse(BaseModel):
    """PLC 복원 응답"""
    plc_id: str = Field(..., description="복원된 PLC ID")
    message: str = Field(..., description="메시지")


class PlcListResponse(BaseModel):
    """PLC 목록 응답"""
    total: int = Field(..., description="전체 개수")
    items: List[PlcResponse] = Field(..., description="PLC 목록")


class PlcSearchResponse(BaseModel):
    """PLC 검색 응답"""
    total: int = Field(..., description="검색 결과 개수")
    items: List[PlcResponse] = Field(..., description="검색 결과")


class PlcCountResponse(BaseModel):
    """PLC 개수 응답"""
    active_count: int = Field(..., description="활성 PLC 개수")
    inactive_count: int = Field(..., description="비활성 PLC 개수")
    total_count: int = Field(..., description="전체 PLC 개수")


class PlcExistsResponse(BaseModel):
    """PLC 존재 여부 응답"""
    plc_id: str = Field(..., description="PLC ID")
    exists: bool = Field(..., description="존재 여부")


class PlcHierarchyResponse(BaseModel):
    """PLC 계층 조회 응답"""
    level: str = Field(..., description="조회한 레벨")
    values: List[str] = Field(..., description="고유 값 목록")
