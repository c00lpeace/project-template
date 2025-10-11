# _*_ coding: utf-8 _*_
"""PLC Service for handling PLC operations."""
import logging
from typing import List, Optional
from ai_backend.database.crud.plc_crud import PLCCrud
from sqlalchemy.orm import Session
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode

logger = logging.getLogger(__name__)


class PlcService:
    """PLC 서비스를 관리하는 클래스"""
    
    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required")
        
        self.db = db
        self.plc_crud = PLCCrud(db)
    
    def create_plc(
        self,
        plc_id: str,
        plant: str,
        process: str,
        line: str,
        equipment_group: str,
        unit: str,
        plc_name: str
    ):
        """PLC 생성"""
        try:
            # PLC ID 중복 체크 (삭제된 것 포함)
            existing_plc = self.plc_crud.get_plc_include_deleted(plc_id)
            if existing_plc:
                if existing_plc.is_active:
                    raise HandledException(
                        ResponseCode.USER_ALREADY_EXISTS,  # PLC_ALREADY_EXISTS로 변경 권장
                        msg=f"PLC ID {plc_id}는 이미 사용 중입니다."
                    )
                else:
                    raise HandledException(
                        ResponseCode.USER_ALREADY_EXISTS,
                        msg=f"PLC ID {plc_id}는 삭제된 상태입니다. 복원을 사용하세요."
                    )
            
            plc = self.plc_crud.create_plc(
                plc_id=plc_id,
                plant=plant,
                process=process,
                line=line,
                equipment_group=equipment_group,
                unit=unit,
                plc_name=plc_name
            )
            return plc
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_plc(self, plc_id: str, include_deleted: bool = False):
        """PLC 조회"""
        try:
            if include_deleted:
                plc = self.plc_crud.get_plc_include_deleted(plc_id)
            else:
                plc = self.plc_crud.get_plc(plc_id)
            
            if not plc:
                raise HandledException(ResponseCode.USER_NOT_FOUND, msg="PLC를 찾을 수 없습니다.")
            
            return plc
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_plcs(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = True,
        plant: Optional[str] = None,
        process: Optional[str] = None,
        line: Optional[str] = None,
        equipment_group: Optional[str] = None,
        unit: Optional[str] = None
    ):
        """PLC 목록 조회"""
        try:
            plcs = self.plc_crud.get_plcs(
                skip=skip,
                limit=limit,
                is_active=is_active,
                plant=plant,
                process=process,
                line=line,
                equipment_group=equipment_group,
                unit=unit
            )
            total_count = self.plc_crud.count_plcs(is_active=is_active)
            return plcs, total_count
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def update_plc(
        self,
        plc_id: str,
        plant: Optional[str] = None,
        process: Optional[str] = None,
        line: Optional[str] = None,
        equipment_group: Optional[str] = None,
        unit: Optional[str] = None,
        plc_name: Optional[str] = None
    ):
        """PLC 정보 수정"""
        try:
            plc = self.plc_crud.update_plc(
                plc_id=plc_id,
                plant=plant,
                process=process,
                line=line,
                equipment_group=equipment_group,
                unit=unit,
                plc_name=plc_name
            )
            if not plc:
                raise HandledException(ResponseCode.USER_NOT_FOUND, msg="PLC를 찾을 수 없습니다.")
            
            return plc
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def delete_plc(self, plc_id: str):
        """PLC 삭제 (소프트 삭제)"""
        try:
            success = self.plc_crud.delete_plc(plc_id)
            if not success:
                raise HandledException(ResponseCode.USER_NOT_FOUND, msg="PLC를 찾을 수 없습니다.")
            
            return True
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def restore_plc(self, plc_id: str):
        """PLC 복원"""
        try:
            success = self.plc_crud.restore_plc(plc_id)
            if not success:
                raise HandledException(ResponseCode.USER_NOT_FOUND, msg="PLC를 찾을 수 없습니다.")
            
            return True
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def exists_plc(self, plc_id: str):
        """PLC 존재 여부 확인"""
        try:
            return self.plc_crud.exists_plc(plc_id)
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def search_plcs(self, keyword: str, skip: int = 0, limit: int = 100, is_active: Optional[bool] = True):
        """PLC 검색"""
        try:
            plcs = self.plc_crud.search_plcs(
                keyword=keyword,
                skip=skip,
                limit=limit,
                is_active=is_active
            )
            return plcs
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_plc_count(self):
        """PLC 개수 조회 (활성/비활성/전체)"""
        try:
            active_count = self.plc_crud.count_plcs(is_active=True)
            inactive_count = self.plc_crud.count_plcs(is_active=False)
            total_count = self.plc_crud.count_plcs(is_active=None)
            
            return {
                'active_count': active_count,
                'inactive_count': inactive_count,
                'total_count': total_count
            }
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
    
    def get_hierarchy_values(
        self,
        level: str,
        plant: Optional[str] = None,
        process: Optional[str] = None,
        line: Optional[str] = None,
        equipment_group: Optional[str] = None
    ):
        """계층별 고유 값 조회"""
        try:
            values = self.plc_crud.get_distinct_values(
                field=level,
                plant=plant,
                process=process,
                line=line,
                equipment_group=equipment_group
            )
            return values
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
