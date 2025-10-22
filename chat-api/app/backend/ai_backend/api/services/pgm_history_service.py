# _*_ coding: utf-8 _*_
"""PGM Mapping History service."""

import logging
from typing import List, Optional, Tuple
from ai_backend.database.crud.pgm_mapping_crud import PgmMappingHistoryCrud
from ai_backend.database.models.pgm_mapping_models import (
    PgmMappingAction,
    PgmMappingHistory,
)
from ai_backend.types.response.exceptions import HandledException
from ai_backend.types.response.response_code import ResponseCode
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PgmHistoryService:
    """매핑 이력 조회 서비스"""

    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session is required")
        self.db = db
        self.pgm_mapping_crud = PgmMappingHistoryCrud(db)

    def get_history_by_id(self, history_id: int) -> PgmMappingHistory:
        """이력 ID로 조회"""
        try:
            history = self.pgm_mapping_crud.get_history_by_id(history_id)
            if not history:
                raise HandledException(
                    ResponseCode.PROGRAM_NOT_FOUND,
                    msg=f"이력 ID '{history_id}'를 찾을 수 없습니다."
                )
            return history
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

    def get_histories_by_plc(
        self,
        plc_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """특정 PLC의 매핑 변경 이력 조회"""
        try:
            histories, total = self.pgm_mapping_crud.get_histories_by_plc(
                plc_id=plc_id,
                skip=skip,
                limit=limit
            )
            logger.info(f"PLC '{plc_id}' 이력 조회: {len(histories)}개")
            return histories, total
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

    def get_histories_by_program(
        self,
        pgm_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """특정 프로그램의 매핑 이력 조회"""
        try:
            histories, total = self.pgm_mapping_crud.get_histories_by_program(
                pgm_id=pgm_id,
                skip=skip,
                limit=limit
            )
            logger.info(f"프로그램 '{pgm_id}' 이력 조회: {len(histories)}개")
            return histories, total
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

    def get_histories_by_user(
        self,
        action_user: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PgmMappingHistory], int]:
        """특정 사용자의 매핑 이력 조회"""
        try:
            histories, total = self.pgm_mapping_crud.get_histories_by_user(
                action_user=action_user,
                skip=skip,
                limit=limit
            )
            logger.info(f"사용자 '{action_user}' 이력 조회: {len(histories)}개")
            return histories, total
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

    def get_recent_histories(
        self,
        skip: int = 0,
        limit: int = 100,
        action: Optional[PgmMappingAction] = None
    ) -> Tuple[List[PgmMappingHistory], int]:
        """최근 매핑 변경 이력 조회 (전체)"""
        try:
            histories, total = self.pgm_mapping_crud.get_recent_histories(
                skip=skip,
                limit=limit,
                action=action
            )
            logger.info(f"전체 이력 조회: {len(histories)}개")
            return histories, total
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)

    def get_history_stats_by_plc(self, plc_id: str) -> dict:
        """특정 PLC의 매핑 이력 통계"""
        try:
            # 전체 이력 조회
            all_histories, total = self.pgm_mapping_crud.get_histories_by_plc(
                plc_id=plc_id,
                skip=0,
                limit=1000  # 충분히 큰 값
            )
            
            # 액션별 카운트
            create_count = sum(1 for h in all_histories if h.action == PgmMappingAction.CREATE.value)
            update_count = sum(1 for h in all_histories if h.action == PgmMappingAction.UPDATE.value)
            delete_count = sum(1 for h in all_histories if h.action == PgmMappingAction.DELETE.value)
            restore_count = sum(1 for h in all_histories if h.action == PgmMappingAction.RESTORE.value)
            
            # 최근 액션
            latest_action = self.pgm_mapping_crud.get_latest_action_by_plc(plc_id)
            
            stats = {
                'plc_id': plc_id,
                'total_changes': total,
                'create_count': create_count,
                'update_count': update_count,
                'delete_count': delete_count,
                'restore_count': restore_count,
                'latest_action': latest_action
            }
            
            logger.info(f"PLC '{plc_id}' 통계: 총 {total}개 변경")
            return stats
        except HandledException:
            raise
        except Exception as e:
            raise HandledException(ResponseCode.UNDEFINED_ERROR, e=e)
