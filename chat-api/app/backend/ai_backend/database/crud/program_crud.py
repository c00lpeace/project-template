# _*_ coding: utf-8 _*_
"""Program CRUD operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ai_backend.database.models.program_models import Program

__all__ = [
    "ProgramCrud",
]


class ProgramCrud:
    """프로그램 CRUD"""
    
    @staticmethod
    def create_program(db: Session, program_data: dict) -> Program:
        """프로그램 생성"""
        program = Program(**program_data)
        db.add(program)
        db.commit()
        db.refresh(program)
        return program
    
    @staticmethod
    def get_program_by_id(db: Session, pgm_id: str) -> Optional[Program]:
        """프로그램 ID로 조회"""
        return db.query(Program).filter(Program.pgm_id == pgm_id).first()
    
    @staticmethod
    def get_programs(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        pgm_version: Optional[str] = None
    ) -> List[Program]:
        """프로그램 목록 조회"""
        query = db.query(Program)
        
        if search:
            query = query.filter(
                (Program.pgm_id.ilike(f"%{search}%")) | 
                (Program.pgm_name.ilike(f"%{search}%"))
            )
        
        if pgm_version:
            query = query.filter(Program.pgm_version == pgm_version)
        
        return query.order_by(Program.create_dt.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_programs(
        db: Session,
        search: Optional[str] = None,
        pgm_version: Optional[str] = None
    ) -> int:
        """프로그램 총 개수"""
        query = db.query(Program)
        
        if search:
            query = query.filter(
                (Program.pgm_id.ilike(f"%{search}%")) | 
                (Program.pgm_name.ilike(f"%{search}%"))
            )
        
        if pgm_version:
            query = query.filter(Program.pgm_version == pgm_version)
        
        return query.count()
    
    @staticmethod
    def update_program(db: Session, pgm_id: str, update_data: dict) -> Optional[Program]:
        """프로그램 수정"""
        program = db.query(Program).filter(Program.pgm_id == pgm_id).first()
        
        if not program:
            return None
        
        for key, value in update_data.items():
            if hasattr(program, key):
                setattr(program, key, value)
        
        program.update_dt = datetime.now()
        db.commit()
        db.refresh(program)
        return program
    
    @staticmethod
    def delete_program(db: Session, pgm_id: str) -> bool:
        """프로그램 삭제"""
        program = db.query(Program).filter(Program.pgm_id == pgm_id).first()
        
        if not program:
            return False
        
        db.delete(program)
        db.commit()
        return True
