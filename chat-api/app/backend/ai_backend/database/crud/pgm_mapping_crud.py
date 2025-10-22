# _*_ coding: utf-8 _*_
"""PLC-Program Mapping CRUD operations."""

from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import datetime
from ai_backend.database.models.pgm_mapping_models import PgmMappingHistory, PgmMappingAction
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
import logging

logger = logging.getLogger(__name__)

class PgmMappingHistoryCrud:
    """
    PLC-프로그램 매핑 이력 CRUD
    새로운 매핑 시스템: PLC_MASTER.pgm_id + PGM_MAPPING_HISTORY
    """

    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required")
        self.db = db

    def create_history(
        self,
        plc_id: str,
        pgm_id: Optional[str],
        action: PgmMappingAction,
        action_user: str,
        prev_pgm_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> PgmMappingHistory:
        """
        매핑 이력 생성
        - plc_crud.py에서 자동으로 호출됨
        """
        try:
            history = PgmMappingHistory(
                plc_id=plc_id,
                pgm_id=pgm_id,
                action=action.value,
                action_dt=datetime.now(),
                action_user=action_user,
                prev_pgm_id=prev_pgm_id,
                notes=notes
            )
            
            self.db.add(history)
            self.db.commit()
            self.db.refresh(history)
            return history
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_history_by_id(self, history_id: int) -> Optional[PgmMappingHistory]:
        """이력 ID로 조회"""
        try:
            return self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.history_id == history_id
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_histories_by_plc(
        self,
        plc_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        특정 PLC의 매핑 변경 이력 조회
        Returns: (이력 목록, 전체 개수)
        """
        try:
            query = self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.plc_id == plc_id
            )
            
            total = query.count()
            histories = query.order_by(
                PgmMappingHistory.action_dt.desc()
            ).offset(skip).limit(limit).all()
            
            return histories, total
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_histories_by_program(
        self,
        pgm_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        특정 프로그램의 매핑 이력 조회
        Returns: (이력 목록, 전체 개수)
        """
        try:
            query = self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.pgm_id == pgm_id
            )
            
            total = query.count()
            histories = query.order_by(
                PgmMappingHistory.action_dt.desc()
            ).offset(skip).limit(limit).all()
            
            return histories, total
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_histories_by_user(
        self,
        action_user: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        특정 사용자의 매핑 이력 조회
        Returns: (이력 목록, 전체 개수)
        """
        try:
            query = self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.action_user == action_user
            )
            
            total = query.count()
            histories = query.order_by(
                PgmMappingHistory.action_dt.desc()
            ).offset(skip).limit(limit).all()
            
            return histories, total
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_recent_histories(
        self,
        skip: int = 0,
        limit: int = 100,
        action: Optional[PgmMappingAction] = None
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        최근 매핑 변경 이력 조회 (전체)
        Returns: (이력 목록, 전체 개수)
        """
        try:
            query = self.db.query(PgmMappingHistory)
            
            if action:
                query = query.filter(PgmMappingHistory.action == action.value)
            
            total = query.count()
            histories = query.order_by(
                PgmMappingHistory.action_dt.desc()
            ).offset(skip).limit(limit).all()
            
            return histories, total
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def count_histories_by_plc(self, plc_id: str) -> int:
        """특정 PLC의 이력 개수"""
        try:
            return self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.plc_id == plc_id
            ).count()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def count_histories_by_program(self, pgm_id: str) -> int:
        """특정 프로그램의 이력 개수"""
        try:
            return self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.pgm_id == pgm_id
            ).count()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def count_histories_by_action(self, action: PgmMappingAction) -> int:
        """특정 액션 타입의 이력 개수"""
        try:
            return self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.action == action.value
            ).count()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def delete_history(self, history_id: int) -> bool:
        """
        이력 삭제
        (*일반적으로 삭제하지 않음)
        """
        try:
            history = self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.history_id == history_id
            ).first()
            
            if not history:
                return False
            
            self.db.delete(history)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_latest_action_by_plc(
        self,
        plc_id: str
    ) -> Optional[PgmMappingHistory]:
        """특정 PLC의 가장 최근 매핑 이력"""
        try:
            return self.db.query(PgmMappingHistory).filter(
                PgmMappingHistory.plc_id == plc_id
            ).order_by(
                PgmMappingHistory.action_dt.desc()
            ).first()
        except Exception as e:
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)
