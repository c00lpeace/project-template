# _*_ coding: utf-8 _*_
"""Program request models."""

from pydantic import BaseModel, Field
from typing import Optional

__all__ = [
    "ProgramCreateRequest",
    "ProgramUpdateRequest",
    "PgmMappingCreateRequest",
    "PgmMappingUpsertRequest",
]


class ProgramCreateRequest(BaseModel):
    """프로그램 생성 요청"""
    pgm_id: str = Field(..., max_length=50, description="프로그램 ID")
    pgm_name: str = Field(..., max_length=200, description="프로그램 명칭")
    document_id: Optional[str] = Field(None, max_length=100, description="문서 ID")
    pgm_version: Optional[str] = Field(None, max_length=20, description="프로그램 버전")
    description: Optional[str] = Field(None, max_length=1000, description="프로그램 설명")
    notes: Optional[str] = Field(None, max_length=1000, description="비고")
    create_user: Optional[str] = Field(None, max_length=50, description="생성자")


class ProgramUpdateRequest(BaseModel):
    """프로그램 수정 요청"""
    pgm_name: Optional[str] = Field(None, max_length=200, description="프로그램 명칭")
    document_id: Optional[str] = Field(None, max_length=100, description="문서 ID")
    pgm_version: Optional[str] = Field(None, max_length=20, description="프로그램 버전")
    description: Optional[str] = Field(None, max_length=1000, description="프로그램 설명")
    notes: Optional[str] = Field(None, max_length=1000, description="비고")
    update_user: Optional[str] = Field(None, max_length=50, description="수정자")


class PgmMappingCreateRequest(BaseModel):
    """매핑 생성 요청"""
    plc_id: str = Field(..., max_length=50, description="PLC ID")
    pgm_id: str = Field(..., max_length=50, description="프로그램 ID")
    notes: Optional[str] = Field(None, max_length=500, description="비고")
    create_user: Optional[str] = Field(None, max_length=50, description="생성자")


class PgmMappingUpsertRequest(BaseModel):
    """매핑 UPSERT 요청 (INSERT or UPDATE)"""
    pgm_id: str = Field(..., max_length=50, description="프로그램 ID")
    notes: Optional[str] = Field(None, max_length=500, description="비고")
    user: Optional[str] = Field(None, max_length=50, description="사용자")
