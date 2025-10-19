# _*_ coding: utf-8 _*_
"""Template Response Models"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class LogicInfo(BaseModel):
    """로직 정보"""
    logic_id: str = Field(..., description="로직 ID")
    logic_name: str = Field(..., description="로직 명칭")
    
    class Config:
        from_attributes = True


class SubFolderInfo(BaseModel):
    """서브 폴더 정보"""
    sub_folder_name: str = Field(..., description="서브 폴더 명칭")
    logic_count: int = Field(..., description="로직 개수")
    logics: List[LogicInfo] = Field(..., description="로직 목록")
    
    class Config:
        from_attributes = True


class FolderInfo(BaseModel):
    """폴더 정보"""
    folder_id: str = Field(..., description="폴더 ID")
    folder_name: str = Field(..., description="폴더 명칭")
    sub_folder_count: int = Field(..., description="서브 폴더 개수")
    total_logic_count: int = Field(..., description="전체 로직 개수")
    sub_folders: List[SubFolderInfo] = Field(..., description="서브 폴더 목록")
    
    class Config:
        from_attributes = True


class TemplateTreeResponse(BaseModel):
    """템플릿 트리 구조 응답"""
    pgm_id: str = Field(..., description="프로그램 ID")
    document_id: Optional[str] = Field(None, description="원본 문서 ID")
    total_count: int = Field(..., description="전체 템플릿 개수")
    folder_count: int = Field(..., description="폴더 개수")
    folders: List[FolderInfo] = Field(..., description="폴더 목록")
    
    class Config:
        from_attributes = True


class TemplateListItem(BaseModel):
    """템플릿 목록 아이템"""
    template_id: int = Field(..., description="템플릿 ID")
    pgm_id: str = Field(..., description="프로그램 ID")
    document_id: Optional[str] = Field(None, description="문서 ID")
    folder_id: str = Field(..., description="폴더 ID")
    folder_name: str = Field(..., description="폴더 명칭")
    sub_folder_name: Optional[str] = Field(None, description="서브 폴더 명칭")
    logic_id: str = Field(..., description="로직 ID")
    logic_name: str = Field(..., description="로직 명칭")
    create_dt: datetime = Field(..., description="생성일시")
    create_user: Optional[str] = Field(None, description="생성자")
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """템플릿 목록 응답"""
    total_count: int = Field(..., description="전체 개수")
    items: List[TemplateListItem] = Field(..., description="템플릿 목록")
    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")
    
    class Config:
        from_attributes = True


class TemplateUploadResult(BaseModel):
    """템플릿 업로드 결과"""
    pgm_id: str = Field(..., description="프로그램 ID")
    document_id: str = Field(..., description="문서 ID")
    total_rows: int = Field(..., description="전체 행 수")
    deleted_count: int = Field(0, description="삭제된 기존 템플릿 수")
    created_count: int = Field(..., description="생성된 템플릿 수")
    
    class Config:
        from_attributes = True


class TemplateSummary(BaseModel):
    """템플릿 요약 정보"""
    pgm_id: str = Field(..., description="프로그램 ID")
    template_count: int = Field(..., description="템플릿 개수")
    folder_count: int = Field(..., description="폴더 개수")
    document_id: Optional[str] = Field(None, description="문서 ID")
    create_dt: Optional[datetime] = Field(None, description="최초 생성일시")
    
    class Config:
        from_attributes = True


class TemplateStatsResponse(BaseModel):
    """템플릿 통계 응답"""
    total_programs: int = Field(..., description="전체 프로그램 수")
    total_templates: int = Field(..., description="전체 템플릿 수")
    programs: List[TemplateSummary] = Field(..., description="프로그램별 요약")
    
    class Config:
        from_attributes = True
