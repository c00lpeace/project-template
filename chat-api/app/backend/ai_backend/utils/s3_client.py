# _*_ coding: utf-8 _*_
"""AWS S3 Client for file storage operations."""
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Client:
    """AWS S3 클라이언트"""
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        bucket_name: str
    ):
        """S3 클라이언트 초기화
        
        Args:
            aws_access_key_id: AWS Access Key ID
            aws_secret_access_key: AWS Secret Access Key
            region_name: AWS Region (예: ap-northeast-2)
            bucket_name: S3 Bucket 이름
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        
        try:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
            logger.info(f"✅ S3 클라이언트 초기화 성공: bucket={bucket_name}, region={region_name}")
        except Exception as e:
            logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
            raise
    
    def upload_file(
        self, 
        file_content: bytes, 
        key: str,
        content_type: Optional[str] = None
    ) -> str:
        """S3에 파일 업로드
        
        Args:
            file_content: 업로드할 파일 내용 (bytes)
            key: S3 object key (경로 포함, 예: uploads/user1/file.pdf)
            content_type: MIME 타입 (예: application/pdf)
        
        Returns:
            S3 URL (https://bucket.s3.region.amazonaws.com/key)
        
        Raises:
            Exception: 업로드 실패 시
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            # S3에 파일 업로드 (put_object 사용)
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                **extra_args
            )
            
            # S3 URL 생성
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}"
            logger.info(f"✅ S3 업로드 성공: {url}")
            return url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(f"❌ S3 업로드 실패 (ClientError): code={error_code}, msg={error_msg}")
            raise Exception(f"S3 업로드 실패: {error_msg}")
        except Exception as e:
            logger.error(f"❌ S3 업로드 실패: {e}")
            raise Exception(f"S3 업로드 실패: {str(e)}")
    
    def download_file(self, key: str) -> bytes:
        """S3에서 파일 다운로드
        
        Args:
            key: S3 object key
        
        Returns:
            파일 내용 (bytes)
        
        Raises:
            Exception: 다운로드 실패 시
        """
        try:
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            file_content = response['Body'].read()
            logger.info(f"✅ S3 다운로드 성공: {key} ({len(file_content)} bytes)")
            return file_content
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.error(f"❌ S3 파일 없음: {key}")
                raise Exception(f"S3에 파일이 존재하지 않습니다: {key}")
            else:
                error_msg = e.response['Error']['Message']
                logger.error(f"❌ S3 다운로드 실패: code={error_code}, msg={error_msg}")
                raise Exception(f"S3 다운로드 실패: {error_msg}")
        except Exception as e:
            logger.error(f"❌ S3 다운로드 실패: {e}")
            raise Exception(f"S3 다운로드 실패: {str(e)}")
    
    def delete_file(self, key: str) -> bool:
        """S3에서 파일 삭제
        
        Args:
            key: S3 object key
        
        Returns:
            삭제 성공 여부
        """
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"✅ S3 삭제 성공: {key}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(f"❌ S3 삭제 실패: code={error_code}, msg={error_msg}")
            return False
        except Exception as e:
            logger.error(f"❌ S3 삭제 실패: {e}")
            return False
    
    def file_exists(self, key: str) -> bool:
        """S3에 파일 존재 여부 확인
        
        Args:
            key: S3 object key
        
        Returns:
            파일 존재 여부
        """
        try:
            self.s3.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False
            logger.warning(f"⚠️ S3 파일 존재 확인 실패: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ S3 파일 존재 확인 실패: {e}")
            return False
    
    def get_file_metadata(self, key: str) -> dict:
        """S3 파일 메타데이터 조회
        
        Args:
            key: S3 object key
        
        Returns:
            메타데이터 딕셔너리 (크기, 타입, 수정일 등)
        """
        try:
            response = self.s3.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            metadata = {
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag', '').strip('"'),
            }
            
            logger.info(f"✅ S3 메타데이터 조회 성공: {key}")
            return metadata
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(f"❌ S3 메타데이터 조회 실패: code={error_code}, msg={error_msg}")
            raise Exception(f"S3 메타데이터 조회 실패: {error_msg}")
        except Exception as e:
            logger.error(f"❌ S3 메타데이터 조회 실패: {e}")
            raise Exception(f"S3 메타데이터 조회 실패: {str(e)}")
