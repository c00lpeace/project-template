# _*_ coding: utf-8 _*_
"""Program request models."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateProgramRequest(BaseModel):
    """프로그램 생성 요청"""
    pgm_id: str = Field(..., min_length=1, max_length=50, description="프로그램 ID")
    pgm_name: str = Field(..., min_length=1, max_length=200, description="프로그램 명칭")
    ladder_doc_id: Optional[str] = Field(None, max_length=100, description="Ladder 문서 ID")
    template_doc_id: Optional[str] = Field(None, max_length=100, description="Template 문서 ID")
    pgm_version: Optional[str] = Field(None, max_length=20, description="프로그램 버전")
    description: Optional[str] = Field(None, max_length=1000, description="프로그램 설명")
    notes: Optional[str] = Field(None, max_length=1000, description="비고")
    create_user: Optional[str] = Field(None, max_length=50, description="생성자")

    @field_validator('pgm_id')
    @classmethod
    def validate_pgm_id(cls, v):
        if not v.strip():
            raise ValueError('프로그램 ID는 공백일 수 없습니다.')
        return v.strip()

    @field_validator('pgm_name')
    @classmethod
    def validate_pgm_name(cls, v):
        if not v.strip():
            raise ValueError('프로그램 명칭은 공백일 수 없습니다.')
        return v.strip()


class UpdateProgramRequest(BaseModel):
    """프로그램 수정 요청"""
    pgm_name: Optional[str] = Field(None, min_length=1, max_length=200, description="프로그램 명칭")
    ladder_doc_id: Optional[str] = Field(None, max_length=100, description="Ladder 문서 ID")
    template_doc_id: Optional[str] = Field(None, max_length=100, description="Template 문서 ID")
    pgm_version: Optional[str] = Field(None, max_length=20, description="프로그램 버전")
    description: Optional[str] = Field(None, max_length=1000, description="프로그램 설명")
    notes: Optional[str] = Field(None, max_length=1000, description="비고")
    update_user: Optional[str] = Field(None, max_length=50, description="수정자")

    @field_validator('pgm_name')
    @classmethod
    def validate_pgm_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('프로그램 명칭은 공백일 수 없습니다.')
        return v.strip() if v else v


class ProgramSearchRequest(BaseModel):
    """프로그램 검색 요청"""
    keyword: str = Field(..., min_length=1, max_length=100, description="검색 키워드 (프로그램 ID 또는 명칭)")
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")
    pgm_version: Optional[str] = Field(None, max_length=20, description="프로그램 버전 필터")

    @field_validator('keyword')
    @classmethod
    def validate_keyword(cls, v):
        if not v.strip():
            raise ValueError('검색 키워드는 공백일 수 없습니다.')
        return v.strip()

    @field_validator('pgm_version')
    @classmethod
    def validate_pgm_version(cls, v):
        if v is not None and not v.strip():
            raise ValueError('프로그램 버전은 공백일 수 없습니다.')
        return v.strip() if v else v


class ProgramListRequest(BaseModel):
    """프로그램 목록 조회 요청"""
    skip: int = Field(0, ge=0, description="건너뛸 개수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 개수")
    pgm_version: Optional[str] = Field(None, max_length=20, description="프로그램 버전 필터")

    @field_validator('pgm_version')
    @classmethod
    def validate_pgm_version(cls, v):
        if v is not None and not v.strip():
            raise ValueError('프로그램 버전은 공백일 수 없습니다.')
        return v.strip() if v else v


class CreateMappingRequest(BaseModel):
    """매핑 생성 요청"""
    plc_id: str = Field(..., min_length=1, max_length=50, description="PLC ID")
    pgm_id: str = Field(..., min_length=1, max_length=50, description="프로그램 ID")
    notes: Optional[str] = Field(None, max_length=500, description="비고")
    create_user: Optional[str] = Field(None, max_length=50, description="생성자")

    @field_validator('plc_id')
    @classmethod
    def validate_plc_id(cls, v):
        if not v.strip():
            raise ValueError('PLC ID는 공백일 수 없습니다.')
        return v.strip()

    @field_validator('pgm_id')
    @classmethod
    def validate_pgm_id(cls, v):
        if not v.strip():
            raise ValueError('프로그램 ID는 공백일 수 없습니다.')
        return v.strip()

class UpsertMappingRequest(BaseModel):
    """매핑 UPSERT 요청 (INSERT or UPDATE)"""
    pgm_id: str = Field(..., min_length=1, max_length=50, description="프로그램 ID")
    notes: Optional[str] = Field(None, max_length=500, description="비고")
    user: Optional[str] = Field(None, max_length=50, description="사용자")

    @field_validator('pgm_id')
    @classmethod
    def validate_pgm_id(cls, v):
        if not v.strip():
            raise ValueError('프로그램 ID는 공백일 수 없습니다.')
        return v.strip()