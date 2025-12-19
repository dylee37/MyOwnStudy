
# books/utils.py

import os
import time
from openai import OpenAI
import numpy as np

# ⭐️ GMS KEY를 환경 변수에서 가져옵니다. ⭐️
# .env 파일에 GMS_KEY="gsk-..." 형태로 저장되어 있어야 합니다.
GMS_API_KEY = os.environ.get("GMS_KEY")

# ⭐️ GMS 엔드포인트 정의 ⭐️
GMS_API_BASE = "https://gms.ssafy.io/gmsapi/"

# API 키는 환경 변수 (OPENAI_API_KEY)에서 자동으로 로드됩니다.
try:
    client = OpenAI(
        api_key=GMS_API_KEY,           # GMS Key 사용
        base_url=GMS_API_BASE + "api.openai.com/v1"       # GMS 엔드포인트 사용
    ) 
except Exception as e:
    print(f"GMS 클라이언트 초기화 실패: API 키 설정 확인 필요. {e}")
    client = None

# 사용할 임베딩 모델 정의
EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text):
    """
    주어진 텍스트에 대해 OpenAI 임베딩 벡터를 생성합니다.
    """
    global client
    if not client:
        return None
        
    if not text:
        return None
    
    try:
        # API 호출 전 호출 빈도 제한을 피하기 위해 잠시 대기
        time.sleep(0.1) 
        
        # OpenAI API 호출
        response = client.embeddings.create(
            input=text.replace("\n", " "),
            model=EMBEDDING_MODEL
        )
        # 벡터 (리스트 형태) 반환
        return response.data[0].embedding
    
    except Exception as e:
        print(f"Error generating embedding for text: {text[:50]}... Error: {e}")
        # 오류 발생 시 상세 로그 출력
        if hasattr(e, 'response') and e.response is not None:
            print(f"API 응답 오류: {e.response.json()}")
        return None

def calculate_cosine_similarity(vector_a, vector_b):
    """
    두 벡터 간의 코사인 유사도를 계산합니다. (NumPy 필요)
    """
    if not vector_a or not vector_b:
        return -1
    
    a = np.array(vector_a)
    b = np.array(vector_b)
    
    # 코사인 유사도 공식: (A · B) / (||A|| * ||B||)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)





# ⭐️ LLM 모델 정의 (Chat 모델 사용) ⭐️
LLM_MODEL = "gpt-4o-mini" # GMS에서 사용 가능한 LLM 모델

def get_llm_recommendation(prompt_message):
    """
    주어진 프롬프트를 LLM에 전달하고 응답을 받습니다.
    """
    global client
    if not client:
        return None
    
    try:
        # LLM 호출
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "당신은 한국 시장의 판매 트렌드를 잘 아는 전문 도서 추천가입니다. 사용자에게 제공된 데이터를 기반으로 가장 판매량이 높을 것으로 예상되는 책의 제목과 저자를 20권 이상 겹치지 않도록 응답하세요. 응답은 오직 JSON 리스트 형태로만 이루어져야 합니다."},
                {"role": "user", "content": prompt_message}
            ],
            # ⭐️ 응답을 JSON 형식으로 강제합니다. ⭐️
            response_format={"type": "json_object"} 
        )
        
        # 응답 텍스트를 JSON으로 파싱하여 반환
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error calling LLM API: {e}")
        return None