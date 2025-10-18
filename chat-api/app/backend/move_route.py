# 임시 스크립트: plc_router.py에서 /plcs/tree를 /plcs/{plc_id} 앞으로 이동
import re

# 파일 읽기
with open(r'D:\project-template\chat-api\app\backend\ai_backend\api\routers\plc_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

# /plcs/tree 엔드포인트 추출
tree_pattern = r'(# =+ ✨ PLC 계층 구조 트리 조회 API.*?(?=@router\.|$))'
tree_match = re.search(tree_pattern, content, re.DOTALL)

if tree_match:
    tree_code = tree_match.group(1)
    
    # tree 코드 제거
    content_without_tree = content.replace(tree_code, '')
    
    # /plcs/{plc_id} 앞에 삽입
    insert_point = content_without_tree.find('@router.get("/plcs/{plc_id}"')
    
    if insert_point > 0:
        # tree 엔드포인트를 /plcs/{plc_id} 앞에 삽입
        new_content = (
            content_without_tree[:insert_point] +
            '\n' + tree_code + '\n' +
            content_without_tree[insert_point:]
        )
        
        # 파일 쓰기
        with open(r'D:\project-template\chat-api\app\backend\ai_backend\api\routers\plc_router.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ /plcs/tree 엔드포인트를 /plcs/{plc_id} 앞으로 이동 완료!")
    else:
        print("❌ /plcs/{plc_id} 엔드포인트를 찾을 수 없습니다.")
else:
    print("❌ /plcs/tree 엔드포인트를 찾을 수 없습니다.")
