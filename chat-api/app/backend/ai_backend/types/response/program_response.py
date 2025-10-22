# _*_ coding: utf-8 _*_
"""Program response models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProgramResponse(BaseModel):
    """프로그램 응답"""
    pgm_id: str
    pgm_name: str
    ladder_doc_id: Optional[str]
    template_doc_id: Optional[str]
    pgm_version: Optional[str]
    description: Optional[str]
    create_dt: datetime
    create_user: Optional[str]
    update_dt: Optional[datetime]
    update_user: Optional[str]
    notes: Optional[str]
    plc_count: Optional[int] = Field(None, description="매핑된 PLC 개수")

    class Config:
        from_attributes = True


class ProgramListResponse(BaseModel):
    """프로그램 목록 응답"""
    items: List[ProgramResponse]
    total_count: int
    page: int
    page_size: int


class ProgramSearchResponse(BaseModel):
    """프로그램 검색 응답"""
    programs: List[ProgramResponse]
    keyword: str
    total_count: int
    skip: int
    limit: int


class ProgramCreateResponse(BaseModel):
    """프로그램 생성 응답"""
    pgm_id: str
    pgm_name: str
    pgm_version: Optional[str]
    message: str = "프로그램이 성공적으로 생성되었습니다."


class ProgramUpdateResponse(BaseModel):
    """프로그램 수정 응답"""
    pgm_id: str
    message: str = "프로그램 정보가 성공적으로 수정되었습니다."


class ProgramDeleteResponse(BaseModel):
    """프로그램 삭제 응답"""
    pgm_id: str
    message: str = "프로그램이 성공적으로 삭제되었습니다."


class ProgramCountResponse(BaseModel):
    """프로그램 수 응답"""
    total_count: int
    version_count: Optional[dict] = Field(None, description="버전별 프로그램 개수")


class ProgramExistsResponse(BaseModel):
    """프로그램 존재 여부 응답"""
    exists: bool
    pgm_id: Optional[str] = None


class PgmMappingResponse(BaseModel):
    """매핑 응답"""
    mapping_id: int
    plc_id: str
    pgm_id: str
    create_dt: datetime
    create_user: Optional[str]
    update_dt: Optional[datetime]
    update_user: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class PgmMappingDetailResponse(BaseModel):
    """매핑 상세 응답 (PLC 및 프로그램 정보 포함)"""
    mapping_id: int
    plc_id: str
    pgm_id: str
    notes: Optional[str]
    create_dt: datetime
    create_user: Optional[str]
    update_dt: Optional[datetime]
    update_user: Optional[str]
    
    # PLC 정보
    plc_name: Optional[str] = None
    plant: Optional[str] = None
    process: Optional[str] = None
    line: Optional[str] = None
    equipment_group: Optional[str] = None
    unit: Optional[str] = None
    
    # 프로그램 정보
    pgm_name: Optional[str] = None
    pgm_version: Optional[str] = None


class PgmMappingListResponse(BaseModel):
    """매핑 목록 응답"""
    mappings: List[PgmMappingDetailResponse]
    total_count: int
    skip: int
    limit: int


class PgmMappingCreateResponse(BaseModel):
    """매핑 생성 응답"""
    mapping_id: int
    plc_id: str
    pgm_id: str
    message: str = "매핑이 성공적으로 생성되었습니다."


class PgmMappingDeleteResponse(BaseModel):
    """매핑 삭제 응답"""
    mapping_id: int
    message: str = "매핑이 성공적으로 삭제되었습니다."