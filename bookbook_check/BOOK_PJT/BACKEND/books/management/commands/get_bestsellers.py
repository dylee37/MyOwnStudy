# books/management/commands/get_bestsellers.py

from django.core.management.base import BaseCommand
from books.models import Book
from books.utils import get_llm_recommendation 
import json
from django.db.models.functions import Cast
from django.db.models import CharField
import random

class Command(BaseCommand):
    help = 'Fetches 20 bestsellers using LLM based on existing book data and updates the DB.' 

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- LLM 기반 베스트셀러 20권 선정 시작 ---'))
        
        # 1-1. LLM 판단에 필요한 최소한의 필드만 포함하여 쿼리
        queryset = Book.objects.values(
            'id', 'title', 'author', 'category__name', 'customer_review_rank'
        ).annotate(
            pub_date=Cast('pub_date', output_field=CharField()) # 날짜 직렬화는 유지
        ).order_by('?') # ⭐️ 랜덤 순서로 정렬하여 무작위성 확보 ⭐️
        
        # 1-2. 전체 쿼리셋을 리스트로 변환하고 200권만 샘플링
        all_books_list = list(queryset)
        
        # ⭐️⭐️ 데이터 샘플링: 200권 또는 전체 중 더 작은 값 선택 ⭐️⭐️
        SAMPLE_SIZE = 200
        if len(all_books_list) > SAMPLE_SIZE:
            sampled_books_data = random.sample(all_books_list, SAMPLE_SIZE)
            self.stdout.write(self.style.WARNING(f"➡️ 프롬프트 크기 축소를 위해 전체 {len(all_books_list)}권 중 {SAMPLE_SIZE}권만 무작위 샘플링합니다."))
        else:
            sampled_books_data = all_books_list


        # 2. LLM에게 전달할 프롬프트 구성
        book_list_str = json.dumps(sampled_books_data, ensure_ascii=False, indent=2)
        prompt = f"""
        당신은 한국 시장의 판매 트렌드를 잘 아는 전문 도서 추천가입니다.
        아래는 시스템에 등록된 도서 {len(sampled_books_data)}권의 **무작위 샘플 목록**입니다.
        이 샘플 데이터와 한국 도서 트렌드를 분석하여 '가장 높은 판매량을 보일 것으로 예상되는' **정확히 20권의 도서**를 선정해 주세요.
        
        규칙:
        1. 응답은 오직 JSON 객체 형태로만 이루어져야 합니다.
        2. JSON 객체는 'bestsellers'라는 키를 가지는 리스트여야 합니다.
        3. 각 리스트 요소는 원본 도서 목록에 있는 'id', 'title', 'author'를 포함해야 합니다.
        4. **반드시 아래 제시된 {len(sampled_books_data)}권의 도서 목록 내에서만 정확히 20권을 선정해야 합니다.**
        
        샘플링된 도서 목록:
        {book_list_str}
        
        응답 예시:
        {{"bestsellers": [ {{"id": 123, "title": "책제목1", "author": "저자1"}}, ... ]}}
        """

        # 3. LLM API 호출
        llm_response_json = get_llm_recommendation(prompt)
        
        if not llm_response_json:
            self.stdout.write(self.style.ERROR('❌ LLM 응답 실패. GMS 키나 네트워크 연결을 확인하세요.'))
            return

        try:
            response_data = json.loads(llm_response_json)
            bestseller_ids = [item['id'] for item in response_data.get('bestsellers', []) if 'id' in item]
            
            if not bestseller_ids:
                self.stdout.write(self.style.ERROR('❌ LLM이 유효한 베스트셀러 ID 목록을 반환하지 않았습니다.'))
                return

            # 4. DB 업데이트: 모든 is_bestseller를 False로 초기화
            Book.objects.all().update(is_bestseller=False)
            
            # 5. 선정된 20권의 is_bestseller를 True로 설정
            Book.objects.filter(id__in=bestseller_ids[:20]).update(is_bestseller=True)
            
            self.stdout.write(self.style.SUCCESS(f'✅ LLM으로부터 {len(bestseller_ids)}권을 선정하여 베스트셀러 20권 등록 완료.'))
        
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'❌ LLM 응답이 JSON 형식이 아닙니다: {llm_response_json[:100]}...'))
        
        self.stdout.write(self.style.SUCCESS('\n--- 베스트셀러 선정 프로세스 종료 ---'))