# _*_ coding: utf-8 _*_
"""PGM Template Models"""
from sqlalchemy import Column, String, Integer, DateTime, Index
from sqlalchemy.sql import func
from ai_backend.database.base import Base


class PgmTemplate(Base):
    """프로그램 구조 템플릿 모델
    
    Excel 파일에서 추출한 프로그램의 폴더/로직 구조를 저장
    """
    __tablename__ = "PGM_TEMPLATE"
    
    # Primary Key
    template_id = Column('TEMPLATE_ID', Integer, primary_key=True, autoincrement=True)
    
    # 문서 연결 (원본 Excel 파일)
    document_id = Column('DOCUMENT_ID', String(100), nullable=True)
    
    # 프로그램 참조
    pgm_id = Column('PGM_ID', String(50), nullable=False)
    
    # 폴더 구조 (3단계 계층)
    folder_id = Column('FOLDER_ID', String(20), nullable=False)
    folder_name = Column('FOLDER_NAME', String(200), nullable=False)
    sub_folder_name = Column('SUB_FOLDER_NAME', String(200), nullable=True)
    
    # 로직 정보
    logic_id = Column('LOGIC_ID', String(20), nullable=False)
    logic_name = Column('LOGIC_NAME', String(200), nullable=False)
    
    # 메타데이터
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)
    
    # 인덱스
    __table_args__ = (
        Index('idx_document_id', 'DOCUMENT_ID'),
        Index('idx_pgm_id', 'PGM_ID'),
        Index('idx_folder_id', 'FOLDER_ID'),
        Index('idx_logic_id', 'LOGIC_ID'),
        Index('idx_pgm_folder_logic', 'PGM_ID', 'FOLDER_ID', 'LOGIC_ID'),
    )
    
    def __repr__(self):
        return (
            f"<PgmTemplate(template_id={self.template_id}, "
            f"pgm_id={self.pgm_id}, folder_id={self.folder_id}, "
            f"logic_id={self.logic_id})>"
        )
