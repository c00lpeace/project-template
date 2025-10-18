"""DB 테이블 구조 확인 스크립트"""
import sys
sys.path.insert(0, 'D:/project-template/chat-api/app/backend')

from sqlalchemy import create_engine, inspect
from ai_backend.config import settings

try:
    # DB 연결 (PostgreSQL)
    db_url = settings.database_url  # Settings의 property 사용
    print(f"DB URL: {db_url}\n")
    engine = create_engine(db_url)
    
    # Inspector로 테이블 확인
    inspector = inspect(engine)
    
    print("=" * 50)
    print("DB 테이블 구조 확인")
    print("=" * 50)
    
    # 모든 테이블 목록
    tables = inspector.get_table_names()
    print(f"\n📋 생성된 테이블 목록 ({len(tables)}개):")
    for table in tables:
        print(f"  - {table}")
    
    # PLC_MASTER 테이블 확인
    print("\n" + "=" * 50)
    if 'PLC_MASTER' in tables:
        print("✅ PLC_MASTER 테이블 존재")
        
        # 컬럼 목록 확인
        columns = inspector.get_columns('PLC_MASTER')
        print(f"\n📋 PLC_MASTER 컬럼 목록 ({len(columns)}개):")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  - {col['name']:20s} {str(col['type']):20s} {nullable}")
        
        # 데이터 개수 확인
        from sqlalchemy import text
        with engine.connect() as conn:
            # PostgreSQL은 대소문자 구분 - 큰따옴표 필요
            result = conn.execute(text('SELECT COUNT(*) as cnt FROM "PLC_MASTER"'))
            count = result.fetchone()[0]
            print(f"\n📊 PLC_MASTER 데이터 개수: {count}개")
            
            if count > 0:
                result = conn.execute(text('SELECT * FROM "PLC_MASTER" LIMIT 3'))
                print("\n📄 샘플 데이터 (최대 3개):")
                for row in result:
                    print(f"  - PLC_ID: {row[0]}, PLANT: {row[1]}")
    else:
        print("❌ PLC_MASTER 테이블이 존재하지 않습니다!")
        print("\n💡 테이블을 생성하려면:")
        print("  1. 서버 시작 시 자동 생성 (base.py의 create_all())")
        print("  2. 또는 수동으로 CREATE TABLE 실행")
    
    print("=" * 50)
    
except Exception as e:
    print(f"❌ 에러 발생: {str(e)}")
    import traceback
    traceback.print_exc()
