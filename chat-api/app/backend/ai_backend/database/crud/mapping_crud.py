# _*_ coding: utf-8 _*_
"""PLC-Program Mapping CRUD operations."""

from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import datetime

from ai_backend.database.models.mapping_models import PgmMappingHistory, MappingAction

__all__ = [
    "PgmMappingHistoryCrud",
]


class PgmMappingHistoryCrud:
    """
    PLC-프로그램 매핑 이력 CRUD
    ✨ 새로운 매핑 시스템: PLC_MASTER.pgm_id + PGM_MAPPING_HISTORY
    """
    
    @staticmethod
    def create_history(
        db: Session,
        plc_id: str,
        pgm_id: Optional[str],
        action: MappingAction,
        action_user: str,
        prev_pgm_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> PgmMappingHistory:
        """
        매핑 이력 생성
        - plc_crud.py에서 자동으로 호출됨
        """
        history = PgmMappingHistory(
            plc_id=plc_id,
            pgm_id=pgm_id,
            action=action.value,
            action_dt=datetime.now(),
            action_user=action_user,
            prev_pgm_id=prev_pgm_id,
            notes=notes
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    
    @staticmethod
    def get_history_by_id(db: Session, history_id: int) -> Optional[PgmMappingHistory]:
        """이력 ID로 조회"""
        return db.query(PgmMappingHistory).filter(
            PgmMappingHistory.history_id == history_id
        ).first()
    
    @staticmethod
    def get_histories_by_plc(
        db: Session,
        plc_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        특정 PLC의 매핑 변경 이력 조회
        Returns: (이력 목록, 전체 개수)
        """
        query = db.query(PgmMappingHistory).filter(
            PgmMappingHistory.plc_id == plc_id
        )
        
        total = query.count()
        
        histories = query.order_by(
            PgmMappingHistory.action_dt.desc()
        ).offset(skip).limit(limit).all()
        
        return histories, total
    
    @staticmethod
    def get_histories_by_program(
        db: Session,
        pgm_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        특정 프로그램의 매핑 이력 조회
        Returns: (이력 목록, 전체 개수)
        """
        query = db.query(PgmMappingHistory).filter(
            PgmMappingHistory.pgm_id == pgm_id
        )
        
        total = query.count()
        
        histories = query.order_by(
            PgmMappingHistory.action_dt.desc()
        ).offset(skip).limit(limit).all()
        
        return histories, total
    
    @staticmethod
    def get_histories_by_user(
        db: Session,
        action_user: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        특정 사용자의 매핑 이력 조회
        Returns: (이력 목록, 전체 개수)
        """
        query = db.query(PgmMappingHistory).filter(
            PgmMappingHistory.action_user == action_user
        )
        
        total = query.count()
        
        histories = query.order_by(
            PgmMappingHistory.action_dt.desc()
        ).offset(skip).limit(limit).all()
        
        return histories, total
    
    @staticmethod
    def get_recent_histories(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        action: Optional[MappingAction] = None
    ) -> Tuple[List[PgmMappingHistory], int]:
        """
        최근 매핑 변경 이력 조회 (전체)
        Returns: (이력 목록, 전체 개수)
        """
        query = db.query(PgmMappingHistory)
        
        if action:
            query = query.filter(PgmMappingHistory.action == action.value)
        
        total = query.count()
        
        histories = query.order_by(
            PgmMappingHistory.action_dt.desc()
        ).offset(skip).limit(limit).all()
        
        return histories, total
    
    @staticmethod
    def count_histories_by_plc(db: Session, plc_id: str) -> int:
        """특정 PLC의 이력 개수"""
        return db.query(PgmMappingHistory).filter(
            PgmMappingHistory.plc_id == plc_id
        ).count()
    
    @staticmethod
    def count_histories_by_program(db: Session, pgm_id: str) -> int:
        """특정 프로그램의 이력 개수"""
        return db.query(PgmMappingHistory).filter(
            PgmMappingHistory.pgm_id == pgm_id
        ).count()
    
    @staticmethod
    def count_histories_by_action(db: Session, action: MappingAction) -> int:
        """특정 액션 타입의 이력 개수"""
        return db.query(PgmMappingHistory).filter(
            PgmMappingHistory.action == action.value
        ).count()
    
    @staticmethod
    def delete_history(db: Session, history_id: int) -> bool:
        """
        이력 삭제
        ⚠️ 주의: 이력은 감사 추적용이므로 일반적으로 삭제하지 않음
        """
        history = db.query(PgmMappingHistory).filter(
            PgmMappingHistory.history_id == history_id
        ).first()
        
        if not history:
            return False
        
        db.delete(history)
        db.commit()
        return True
    
    @staticmethod
    def get_latest_action_by_plc(
        db: Session,
        plc_id: str
    ) -> Optional[PgmMappingHistory]:
        """특정 PLC의 가장 최근 매핑 이력"""
        return db.query(PgmMappingHistory).filter(
            PgmMappingHistory.plc_id == plc_id
        ).order_by(
            PgmMappingHistory.action_dt.desc()
        ).first()
