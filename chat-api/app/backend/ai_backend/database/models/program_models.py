# _*_ coding: utf-8 _*_
"""Program and PGM Mapping models."""

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql.expression import func
from ai_backend.database.base import Base

__all__ = [
    "Program",
    "PgmMapping",
]


class Program(Base):
    """프로그램 마스터 테이블"""
    __tablename__ = "PROGRAMS"
    
    pgm_id = Column('PGM_ID', String(50), primary_key=True)
    pgm_name = Column('PGM_NAME', String(200), nullable=False)
    document_id = Column('DOCUMENT_ID', String(100), nullable=True)
    pgm_version = Column('PGM_VERSION', String(20), nullable=True)
    description = Column('DESCRIPTION', String(1000), nullable=True)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)
    update_dt = Column('UPDATE_DT', DateTime, nullable=True, onupdate=func.now())
    update_user = Column('UPDATE_USER', String(50), nullable=True)
    notes = Column('NOTES', String(1000), nullable=True)


class PgmMapping(Base):
    """PLC-프로그램 매핑 테이블 (N:1 관계)"""
    __tablename__ = "PGM_MAPPING"
    
    mapping_id = Column('MAPPING_ID', Integer, primary_key=True, autoincrement=True)
    plc_id = Column('PLC_ID', String(50), unique=True, nullable=False, index=True)
    pgm_id = Column('PGM_ID', String(50), nullable=False, index=True)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)
    update_dt = Column('UPDATE_DT', DateTime, nullable=True, onupdate=func.now())
    update_user = Column('UPDATE_USER', String(50), nullable=True)
    notes = Column('NOTES', String(500), nullable=True)
