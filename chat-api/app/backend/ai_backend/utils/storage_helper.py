# _*_ coding: utf-8 _*_
"""Storage Helper - S3/로컬 스토리지 통합 유틸리티"""

import io
import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Dict

logger = logging.getLogger(__name__)


class StorageHelper:
    """S3/로컬 스토리지 통합 헬퍼 클래스
    
    S3와 로컬 스토리지를 추상화하여 동일한 인터페이스로 파일 접근 제공
    
    Features:
        - S3/로컬 자동 판단 (metadata_json.storage_type 기반)
        - 메모리 기반 처리 (BytesIO)
        - 임시 파일 다운로드 (자동 정리)
        - 싱글톤 S3 클라이언트
    
    Usage:
        # 메모리 스트림
        stream = StorageHelper.get_file_stream(document)
        df = pd.read_excel(stream)
        
        # 임시 파일
        with StorageHelper.download_to_temp(document) as path:
            df = pd.read_excel(path)
    """
    
    # 싱글톤 S3 클라이언트
    _s3_client = None
    
    @classmethod
    def _get_s3_client(cls):
        """S3 클라이언트 싱글톤 인스턴스 반환
        
        Returns:
            S3Client 인스턴스
        """
        if cls._s3_client is None:
            try:
                from ai_backend.config.simple_settings import settings
                from ai_backend.utils.s3_client import S3Client
                
                cls._s3_client = S3Client(
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region,
                    bucket_name=settings.s3_bucket_name
                )
                logger.info("✅ S3 클라이언트 초기화 완료 (StorageHelper)")
            except Exception as e:
                logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
                raise
        
        return cls._s3_client
    
    @classmethod
    def get_file_bytes(cls, document: Dict) -> bytes:
        """파일을 bytes로 다운로드
        
        Args:
            document: 문서 딕셔너리 (metadata_json 포함)
                - metadata_json.storage_type: 's3' or 'local'
                - metadata_json.s3_key: S3 키 (S3인 경우)
                - upload_path or file_path: 로컬 경로 (로컬인 경우)
        
        Returns:
            파일 내용 (bytes)
        
        Raises:
            Exception: 파일 읽기 실패 시
        """
        try:
            # storage_type 확인
            metadata_json = document.get('metadata_json', {})
            storage_type = metadata_json.get('storage_type', 'local')
            
            if storage_type == 's3':
                # S3에서 다운로드
                s3_key = metadata_json.get('s3_key')
                if not s3_key:
                    raise ValueError("S3 storage_type이지만 s3_key가 없습니다")
                
                s3_client = cls._get_s3_client()
                file_bytes = s3_client.download_file(s3_key)
                logger.info(f"✅ S3 다운로드 완료: {s3_key} ({len(file_bytes):,} bytes)")
                return file_bytes
            
            else:
                # 로컬에서 읽기
                file_path = document.get('upload_path') or document.get('file_path')
                if not file_path:
                    raise ValueError("로컬 storage_type이지만 file_path가 없습니다")
                
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
                logger.info(f"✅ 로컬 파일 읽기 완료: {file_path} ({len(file_bytes):,} bytes)")
                return file_bytes
        
        except Exception as e:
            logger.error(f"❌ 파일 읽기 실패: {e}")
            raise
    
    @classmethod
    def get_file_stream(cls, document: Dict) -> BinaryIO:
        """파일을 BytesIO 스트림으로 반환
        
        메모리 기반으로 파일을 읽어서 BytesIO 스트림으로 반환.
        pandas, PIL 등에서 직접 사용 가능.
        
        Args:
            document: 문서 딕셔너리
        
        Returns:
            BytesIO 스트림 (파일 포인터는 0에 위치)
        
        Example:
            stream = StorageHelper.get_file_stream(document)
            df = pd.read_excel(stream)
        """
        try:
            file_bytes = cls.get_file_bytes(document)
            stream = io.BytesIO(file_bytes)
            logger.info(f"✅ BytesIO 스트림 생성 완료: {len(file_bytes):,} bytes")
            return stream
        
        except Exception as e:
            logger.error(f"❌ 스트림 생성 실패: {e}")
            raise
    
    @classmethod
    @contextmanager
    def download_to_temp(cls, document: Dict, suffix: str = None):
        """파일을 임시 디렉토리에 다운로드 (자동 정리)
        
        Context Manager를 사용하여 임시 파일을 생성하고,
        with 블록 종료 시 자동으로 삭제.
        
        Args:
            document: 문서 딕셔너리
            suffix: 파일 확장자 (예: '.xlsx', '.zip')
                   None이면 원본 파일명에서 자동 추출
        
        Yields:
            임시 파일 경로 (str)
        
        Example:
            with StorageHelper.download_to_temp(document, suffix='.xlsx') as path:
                df = pd.read_excel(path)
                # 처리...
            # with 블록 종료 시 임시 파일 자동 삭제
        """
        # 확장자 자동 추출
        if suffix is None:
            filename = document.get('original_filename') or document.get('filename', '')
            suffix = Path(filename).suffix or '.tmp'
        
        # 임시 파일 생성
        tmp_file = None
        try:
            # 파일 다운로드
            file_bytes = cls.get_file_bytes(document)
            
            # 임시 파일에 쓰기 (delete=False로 수동 관리)
            tmp_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False
            )
            tmp_file.write(file_bytes)
            tmp_file.flush()
            tmp_file.close()
            
            tmp_path = tmp_file.name
            logger.info(f"✅ 임시 파일 생성: {tmp_path} ({len(file_bytes):,} bytes)")
            
            # 경로 반환
            yield tmp_path
        
        finally:
            # 자동 정리
            if tmp_file and tmp_file.name:
                try:
                    Path(tmp_file.name).unlink()
                    logger.info(f"✅ 임시 파일 삭제: {tmp_file.name}")
                except Exception as e:
                    logger.warning(f"⚠️ 임시 파일 삭제 실패: {tmp_file.name}, {e}")
    
    @classmethod
    def get_file_text(cls, document: Dict, encoding: str = 'utf-8') -> str:
        """텍스트 파일 내용 반환
        
        Args:
            document: 문서 딕셔너리
            encoding: 인코딩 (기본값: utf-8)
        
        Returns:
            텍스트 내용 (str)
        
        Example:
            text = StorageHelper.get_file_text(document)
        """
        try:
            file_bytes = cls.get_file_bytes(document)
            text = file_bytes.decode(encoding)
            logger.info(f"✅ 텍스트 파일 읽기 완료: {len(text):,} chars")
            return text
        
        except Exception as e:
            logger.error(f"❌ 텍스트 파일 읽기 실패: {e}")
            raise
