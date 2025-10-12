# _*_ coding: utf-8 _*_
"""Program and PGM Mapping CRUD operations."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ai_backend.database.models.program_models import Program, PgmMapping

__all__ = [
    "ProgramCrud",
    "PgmMappingCrud",
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


class PgmMappingCrud:
    """PLC-프로그램 매핑 CRUD"""
    
    @staticmethod
    def create_mapping(db: Session, mapping_data: dict) -> PgmMapping:
        """매핑 생성"""
        mapping = PgmMapping(**mapping_data)
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return mapping
    
    @staticmethod
    def get_mapping_by_plc_id(db: Session, plc_id: str) -> Optional[PgmMapping]:
        """PLC ID로 매핑 조회"""
        return db.query(PgmMapping).filter(PgmMapping.plc_id == plc_id).first()
    
    @staticmethod
    def get_mapping_by_id(db: Session, mapping_id: int) -> Optional[PgmMapping]:
        """매핑 ID로 조회"""
        return db.query(PgmMapping).filter(PgmMapping.mapping_id == mapping_id).first()
    
    @staticmethod
    def get_mappings(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        plc_id: Optional[str] = None,
        pgm_id: Optional[str] = None
    ) -> List[PgmMapping]:
        """매핑 목록 조회"""
        query = db.query(PgmMapping)
        
        if plc_id:
            query = query.filter(PgmMapping.plc_id == plc_id)
        
        if pgm_id:
            query = query.filter(PgmMapping.pgm_id == pgm_id)
        
        return query.order_by(PgmMapping.create_dt.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_mappings(
        db: Session,
        plc_id: Optional[str] = None,
        pgm_id: Optional[str] = None
    ) -> int:
        """매핑 총 개수"""
        query = db.query(PgmMapping)
        
        if plc_id:
            query = query.filter(PgmMapping.plc_id == plc_id)
        
        if pgm_id:
            query = query.filter(PgmMapping.pgm_id == pgm_id)
        
        return query.count()
    
    @staticmethod
    def count_mappings_by_pgm_id(db: Session, pgm_id: str) -> int:
        """특정 프로그램에 매핑된 PLC 개수"""
        return db.query(PgmMapping).filter(PgmMapping.pgm_id == pgm_id).count()
    
    @staticmethod
    def upsert_mapping(db: Session, plc_id: str, mapping_data: dict) -> PgmMapping:
        """
        매핑 UPSERT (INSERT or UPDATE)
        - PLC_ID가 이미 존재하면 UPDATE
        - PLC_ID가 없으면 INSERT
        """
        existing = db.query(PgmMapping).filter(PgmMapping.plc_id == plc_id).first()
        
        if existing:
            # UPDATE
            existing.pgm_id = mapping_data.get('pgm_id', existing.pgm_id)
            existing.notes = mapping_data.get('notes', existing.notes)
            existing.update_user = mapping_data.get('update_user')
            existing.update_dt = datetime.now()
        else:
            # INSERT
            existing = PgmMapping(
                plc_id=plc_id,
                pgm_id=mapping_data['pgm_id'],
                create_user=mapping_data.get('create_user'),
                notes=mapping_data.get('notes')
            )
            db.add(existing)
        
        db.commit()
        db.refresh(existing)
        return existing
    
    @staticmethod
    def delete_mapping(db: Session, mapping_id: int) -> bool:
        """매핑 삭제 (매핑 ID로)"""
        mapping = db.query(PgmMapping).filter(PgmMapping.mapping_id == mapping_id).first()
        
        if not mapping:
            return False
        
        db.delete(mapping)
        db.commit()
        return True
    
    @staticmethod
    def delete_mapping_by_plc_id(db: Session, plc_id: str) -> bool:
        """매핑 삭제 (PLC ID로)"""
        mapping = db.query(PgmMapping).filter(PgmMapping.plc_id == plc_id).first()
        
        if not mapping:
            return False
        
        db.delete(mapping)
        db.commit()
        return True
