# _*_ coding: utf-8 _*_
"""PLC CRUD operations with database."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List
from datetime import datetime
from ai_backend.database.models.plc_models import PLCMaster
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
import logging

logger = logging.getLogger(__name__)


class PLCCrud:
    """PLC 관련 CRUD 작업을 처리하는 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plc(
        self,
        plc_id: str,
        plant: str,
        process: str,
        line: str,
        equipment_group: str,
        unit: str,
        plc_name: str
    ) -> PLCMaster:
        """PLC 생성 (IS_ACTIVE=TRUE)"""
        try:
            plc = PLCMaster(
                plc_id=plc_id,
                plant=plant,
                process=process,
                line=line,
                equipment_group=equipment_group,
                unit=unit,
                plc_name=plc_name,
                create_dt=datetime.now(),
                is_active=True
            )
            self.db.add(plc)
            self.db.commit()
            self.db.refresh(plc)
            return plc
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"PLC 생성 실패 (중복 키): {str(e)}")
            raise HandledException(ResponseCode.DATABASE_INTEGRITY_ERROR, e=e)
        except Exception as e:
            self.db.rollback()
            logger.error(f"PLC 생성 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_plc(self, plc_id: str) -> Optional[PLCMaster]:
        """PLC 조회 (활성 상태만)"""
        try:
            return self.db.query(PLCMaster).filter(
                and_(
                    PLCMaster.plc_id == plc_id,
                    PLCMaster.is_active == True
                )
            ).first()
        except Exception as e:
            logger.error(f"PLC 조회 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_plc_include_deleted(self, plc_id: str) -> Optional[PLCMaster]:
        """PLC 조회 (삭제된 것 포함)"""
        try:
            return self.db.query(PLCMaster).filter(
                PLCMaster.plc_id == plc_id
            ).first()
        except Exception as e:
            logger.error(f"PLC 조회 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
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
    ) -> List[PLCMaster]:
        """PLC 목록 조회 (필터링 지원)"""
        try:
            query = self.db.query(PLCMaster)
            
            # 활성 상태 필터
            if is_active is not None:
                query = query.filter(PLCMaster.is_active == is_active)
            
            # 계층 구조 필터
            if plant:
                query = query.filter(PLCMaster.plant == plant)
            if process:
                query = query.filter(PLCMaster.process == process)
            if line:
                query = query.filter(PLCMaster.line == line)
            if equipment_group:
                query = query.filter(PLCMaster.equipment_group == equipment_group)
            if unit:
                query = query.filter(PLCMaster.unit == unit)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"PLC 목록 조회 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def count_plcs(self, is_active: Optional[bool] = True) -> int:
        """PLC 개수 조회"""
        try:
            query = self.db.query(PLCMaster)
            if is_active is not None:
                query = query.filter(PLCMaster.is_active == is_active)
            return query.count()
        except Exception as e:
            logger.error(f"PLC 개수 조회 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def update_plc(
        self,
        plc_id: str,
        plant: Optional[str] = None,
        process: Optional[str] = None,
        line: Optional[str] = None,
        equipment_group: Optional[str] = None,
        unit: Optional[str] = None,
        plc_name: Optional[str] = None
    ) -> Optional[PLCMaster]:
        """PLC 정보 수정"""
        try:
            plc = self.get_plc(plc_id)
            if not plc:
                return None
            
            # 변경된 필드만 업데이트
            if plant is not None:
                plc.plant = plant
            if process is not None:
                plc.process = process
            if line is not None:
                plc.line = line
            if equipment_group is not None:
                plc.equipment_group = equipment_group
            if unit is not None:
                plc.unit = unit
            if plc_name is not None:
                plc.plc_name = plc_name
            
            plc.update_dt = datetime.now()
            
            self.db.commit()
            self.db.refresh(plc)
            return plc
        except Exception as e:
            self.db.rollback()
            logger.error(f"PLC 수정 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def delete_plc(self, plc_id: str) -> bool:
        """PLC 삭제 (소프트 삭제: IS_ACTIVE=FALSE)"""
        try:
            plc = self.get_plc(plc_id)
            if not plc:
                return False
            
            plc.is_active = False
            plc.update_dt = datetime.now()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"PLC 삭제 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def restore_plc(self, plc_id: str) -> bool:
        """PLC 복원 (IS_ACTIVE=TRUE)"""
        try:
            plc = self.get_plc_include_deleted(plc_id)
            if not plc:
                return False
            
            plc.is_active = True
            plc.update_dt = datetime.now()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"PLC 복원 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def exists_plc(self, plc_id: str) -> bool:
        """PLC 존재 여부 확인 (활성 상태만)"""
        try:
            return self.db.query(PLCMaster).filter(
                and_(
                    PLCMaster.plc_id == plc_id,
                    PLCMaster.is_active == True
                )
            ).count() > 0
        except Exception as e:
            logger.error(f"PLC 존재 확인 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def search_plcs(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = True
    ) -> List[PLCMaster]:
        """PLC 검색 (PLC_ID, PLC_NAME)"""
        try:
            query = self.db.query(PLCMaster)
            
            if is_active is not None:
                query = query.filter(PLCMaster.is_active == is_active)
            
            # PLC_ID 또는 PLC_NAME에서 검색
            query = query.filter(
                or_(
                    PLCMaster.plc_id.ilike(f"%{keyword}%"),
                    PLCMaster.plc_name.ilike(f"%{keyword}%")
                )
            )
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"PLC 검색 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
    
    def get_distinct_values(
        self,
        field: str,
        plant: Optional[str] = None,
        process: Optional[str] = None,
        line: Optional[str] = None,
        equipment_group: Optional[str] = None
    ) -> List[str]:
        """계층별 고유 값 조회 (예: Plant 목록, 공정 목록 등)"""
        try:
            query = self.db.query(PLCMaster).filter(PLCMaster.is_active == True)
            
            # 상위 계층 필터
            if plant:
                query = query.filter(PLCMaster.plant == plant)
            if process:
                query = query.filter(PLCMaster.process == process)
            if line:
                query = query.filter(PLCMaster.line == line)
            if equipment_group:
                query = query.filter(PLCMaster.equipment_group == equipment_group)
            
            # 필드별 고유 값 추출
            if field == "plant":
                results = query.distinct(PLCMaster.plant).all()
                return [r.plant for r in results]
            elif field == "process":
                results = query.distinct(PLCMaster.process).all()
                return [r.process for r in results]
            elif field == "line":
                results = query.distinct(PLCMaster.line).all()
                return [r.line for r in results]
            elif field == "equipment_group":
                results = query.distinct(PLCMaster.equipment_group).all()
                return [r.equipment_group for r in results]
            elif field == "unit":
                results = query.distinct(PLCMaster.unit).all()
                return [r.unit for r in results]
            else:
                return []
        except Exception as e:
            logger.error(f"고유 값 조회 실패: {str(e)}")
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
