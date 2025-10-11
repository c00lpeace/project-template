# _*_ coding: utf-8 _*_
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql.expression import func, true
from ai_backend.database.base import Base

__all__ = [
    "PLCMaster",
]

class PLCMaster(Base):
    __tablename__ = "PLC_MASTER"
    
    plc_id = Column('PLC_ID', String(50), primary_key=True)  # PLC ID (예: M1CFB01000)
    plant = Column('PLANT', String(100), nullable=False)  # Plant
    process = Column('PROCESS', String(100), nullable=False)  # 공정
    line = Column('LINE', String(100), nullable=False)  # Line
    equipment_group = Column('EQUIPMENT_GROUP', String(100), nullable=False)  # 장비그룹
    unit = Column('UNIT', String(100), nullable=False)  # 호기
    plc_name = Column('PLC_NAME', String(200), nullable=False)  # PLC 명칭
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())  # 활성 상태 (삭제 = FALSE)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())  # 생성일시
    update_dt = Column('UPDATE_DT', DateTime, nullable=True)  # 수정일시
