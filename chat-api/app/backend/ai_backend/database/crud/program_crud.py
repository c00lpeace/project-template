# _*_ coding: utf-8 _*_
"""Program CRUD operations with database."""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ai_backend.database.models.program_models import Program
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
import logging

logger = logging.getLogger(__name__)


class ProgramCRUD:
    """프로그램 관련 CRUD 작업을 처리하는 클래스"""

    def __init__(self, db: Session):
        self.db = db

    def create_program(
        self,
        program_data: dict
    ) -> Program:
        """프로그램 생성"""
        try:
            program = Program(**program_data)
            self.db.add(program)
            self.db.commit()
            self.db.refresh(program)
            return program
        except Exception as e:
            self.db.rollback()
            logger.error(str(e))
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_program_by_id(self, pgm_id: str) -> Optional[Program]:
        """프로그램 ID로 조회"""
        try:
            return self.db.query(Program).filter(Program.pgm_id == pgm_id).first()
        except Exception as e:
            logger.error(str(e))
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def get_programs(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        pgm_version: Optional[str] = None
    ) -> List[Program]:
        """프로그램 목록 조회"""
        try:
            query = self.db.query(Program)
            
            if search:
                query = query.filter(
                    (Program.pgm_id.ilike(f"%{search}%")) |
                    (Program.pgm_name.ilike(f"%{search}%"))
                )
            
            if pgm_version:
                query = query.filter(Program.pgm_version == pgm_version)
            
            return query.order_by(Program.create_dt.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(str(e))
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def count_programs(
        self,
        search: Optional[str] = None,
        pgm_version: Optional[str] = None
    ) -> int:
        """프로그램 총 개수"""
        try:
            query = self.db.query(Program)
            
            if search:
                query = query.filter(
                    (Program.pgm_id.ilike(f"%{search}%")) |
                    (Program.pgm_name.ilike(f"%{search}%"))
                )
            
            if pgm_version:
                query = query.filter(Program.pgm_version == pgm_version)
            
            return query.count()
        except Exception as e:
            logger.error(str(e))
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def update_program(
        self,
        pgm_id: str,
        update_data: dict
    ) -> Optional[Program]:
        """프로그램 수정"""
        try:
            program = self.db.query(Program).filter(Program.pgm_id == pgm_id).first()
            
            if not program:
                return None
            
            for key, value in update_data.items():
                if hasattr(program, key):
                    setattr(program, key, value)
            
            program.update_dt = datetime.now()
            self.db.commit()
            self.db.refresh(program)
            return program
        except Exception as e:
            self.db.rollback()
            logger.error(str(e))
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)

    def delete_program(self, pgm_id: str) -> bool:
        """프로그램 삭제"""
        try:
            program = self.db.query(Program).filter(Program.pgm_id == pgm_id).first()
            
            if not program:
                return False
            
            self.db.delete(program)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(str(e))
            raise HandledException(ResponseCode.DATABASE_QUERY_ERROR, e=e)