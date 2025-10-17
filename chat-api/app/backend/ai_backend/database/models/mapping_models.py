# _*_ coding: utf-8 _*_
"""PLC-Program Mapping models."""

import enum
from ai_backend.database.base import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql.expression import func

__all__ = [
    "PgmMappingHistory",
    "MappingAction",
]


class MappingAction(str, enum.Enum):
    """매핑 액션 타입"""
    CREATE = "CREATE"    # 최초 매핑
    UPDATE = "UPDATE"    # 프로그램 변경
    DELETE = "DELETE"    # 매핑 해제
    RESTORE = "RESTORE"  # 매핑 복원


class PgmMappingHistory(Base):
    """
    PLC-프로그램 매핑 이력 테이블
    - 모든 매핑 변경 이력을 시간순으로 기록
    - PLC_MASTER.pgm_id는 현재 상태, 이 테이블은 전체 이력
    """
    __tablename__ = "PGM_MAPPING_HISTORY"
    
    history_id = Column('HISTORY_ID', Integer, primary_key=True, autoincrement=True)
    plc_id = Column('PLC_ID', String(50), nullable=False, index=True)
    pgm_id = Column('PGM_ID', String(50), nullable=True)
    
    # 이력 메타데이터
    action = Column('ACTION', String(20), nullable=False)
    action_dt = Column('ACTION_DT', DateTime, nullable=False, server_default=func.now(), index=True)
    action_user = Column('ACTION_USER', String(50), nullable=True)
    
    # 변경 전 정보
    prev_pgm_id = Column('PREV_PGM_ID', String(50), nullable=True)
    
    # 비고
    notes = Column('NOTES', String(500), nullable=True)
    
    __table_args__ = (
        {'comment': 'PLC-프로그램 매핑 변경 이력 (감사 추적용)'}
    )
