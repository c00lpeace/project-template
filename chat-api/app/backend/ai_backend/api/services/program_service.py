# _*_ coding: utf-8 _*_
"""Program service."""

from sqlalchemy.orm import Session
from ai_backend.database.crud.program_crud import ProgramCrud
from ai_backend.database.models.program_models import Program
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class ProgramService:
    """프로그램 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_program(
        self,
        pgm_id: str,
        pgm_name: str,
        document_id: Optional[str] = None,
        pgm_version: Optional[str] = None,
        description: Optional[str] = None,
        create_user: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Program:
        """프로그램 생성"""
        # 중복 체크
        existing = ProgramCrud.get_program_by_id(self.db, pgm_id)
        if existing:
            raise HandledException(
                resp_code=ResponseCode.PROGRAM_ALREADY_EXISTS,
                msg=f"프로그램 ID '{pgm_id}'가 이미 존재합니다."
            )
        
        program_data = {
            'pgm_id': pgm_id,
            'pgm_name': pgm_name,
            'document_id': document_id,
            'pgm_version': pgm_version,
            'description': description,
            'create_user': create_user,
            'notes': notes
        }
        
        program = ProgramCrud.create_program(self.db, program_data)
        logger.info(f"프로그램 생성: {pgm_id}")
        return program
    
    def get_program(self, pgm_id: str) -> Program:
        """프로그램 조회"""
        program = ProgramCrud.get_program_by_id(self.db, pgm_id)
        if not program:
            raise HandledException(
                resp_code=ResponseCode.PROGRAM_NOT_FOUND,
                msg=f"프로그램 ID '{pgm_id}'를 찾을 수 없습니다."
            )
        return program
    
    def get_programs(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        pgm_version: Optional[str] = None
    ) -> tuple[List[Program], int]:
        """프로그램 목록 조회"""
        programs = ProgramCrud.get_programs(
            db=self.db,
            skip=skip,
            limit=limit,
            search=search,
            pgm_version=pgm_version
        )
        total = ProgramCrud.count_programs(
            db=self.db,
            search=search,
            pgm_version=pgm_version
        )
        return programs, total
    
    def update_program(
        self,
        pgm_id: str,
        pgm_name: Optional[str] = None,
        document_id: Optional[str] = None,
        pgm_version: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        update_user: Optional[str] = None
    ) -> Program:
        """프로그램 수정"""
        # 존재 여부 확인
        existing = ProgramCrud.get_program_by_id(self.db, pgm_id)
        if not existing:
            raise HandledException(
                resp_code=ResponseCode.PROGRAM_NOT_FOUND,
                msg=f"프로그램 ID '{pgm_id}'를 찾을 수 없습니다."
            )
        
        # 수정 데이터 준비
        update_data = {}
        if pgm_name is not None:
            update_data['pgm_name'] = pgm_name
        if document_id is not None:
            update_data['document_id'] = document_id
        if pgm_version is not None:
            update_data['pgm_version'] = pgm_version
        if description is not None:
            update_data['description'] = description
        if notes is not None:
            update_data['notes'] = notes
        if update_user is not None:
            update_data['update_user'] = update_user
        
        program = ProgramCrud.update_program(self.db, pgm_id, update_data)
        logger.info(f"프로그램 수정: {pgm_id}")
        return program
    
    def delete_program(self, pgm_id: str) -> bool:
        """프로그램 삭제"""
        # 존재 여부 확인
        existing = ProgramCrud.get_program_by_id(self.db, pgm_id)
        if not existing:
            raise HandledException(
                resp_code=ResponseCode.PROGRAM_NOT_FOUND,
                msg=f"프로그램 ID '{pgm_id}'를 찾을 수 없습니다."
            )
        
        # 삭제 실행
        success = ProgramCrud.delete_program(self.db, pgm_id)
        if success:
            logger.info(f"프로그램 삭제: {pgm_id}")
        return success
