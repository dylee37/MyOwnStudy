from django.core.management.base import BaseCommand
from books.models import Book
from books.utils import get_embedding # 우리가 작성한 utils 함수 임포트
import os

class Command(BaseCommand):
    # 이 'help' 문자열이 명령어 설명으로 나타납니다.
    help = 'Generate and save embeddings for all books using OpenAI API.' 

    def handle(self, *args, **options):

        # ⭐️⭐️ 디버깅 코드 수정: 뒷 8자리 출력 ⭐️⭐️
        loaded_key = os.environ.get("GMS_KEY", "GMS_KEY_NOT_SET")
        
        if loaded_key != "GMS_KEY_NOT_SET" and len(loaded_key) > 8:
            display_key = loaded_key[-8:] # 문자열의 마지막 8자리
            self.stdout.write(self.style.WARNING(f"➡️ 현재 Django가 로드한 GMS Key의 뒷 8자리: ...{display_key}"))
        else:
            self.stdout.write(self.style.WARNING("➡️ GMS Key가 로드되지 않았거나 너무 짧습니다."))
        # ⭐️⭐️ 디버깅 코드 끝 ⭐️⭐️

        self.stdout.write(self.style.SUCCESS('--- 임베딩 생성 시작 (OpenAI API 호출) ---'))
        
        # 아직 임베딩이 없는 책만 필터링하여 대상
        books = Book.objects.filter(embedding_vector__isnull=True) 
        total_books_to_process = books.count()
        processed_count = 0
        
        self.stdout.write(f'총 처리할 책 권수: {total_books_to_process}권')
        
        if total_books_to_process == 0:
            self.stdout.write(self.style.SUCCESS('모든 책에 이미 임베딩이 저장되어 있습니다.'))
            return

        for book in books:
            # ⭐️ 임베딩을 생성할 텍스트 조합 ⭐️
            text_to_embed = (
                f"제목: {book.title}. "
                f"부제: {book.subTitle}. "
                f"저자: {book.author}. "
                f"출판사: {book.publisher}. "
                f"카테고리: {book.category.name if book.category else 'N/A'}. "
                f"내용 요약: {book.description}"
            )
            
            embedding = get_embedding(text_to_embed)
            
            if embedding:
                # DB에 저장
                book.embedding_vector = embedding
                book.save()
                processed_count += 1
                self.stdout.write(f'✅ {processed_count}/{total_books_to_process} - {book.title[:30]}... 임베딩 저장 완료')
            else:
                self.stdout.write(self.style.ERROR(f'❌ {book.title[:30]}... 임베딩 생성 실패 (API 에러 또는 텍스트 없음)'))
            
        self.stdout.write(self.style.SUCCESS(f'\n--- 임베딩 생성 완료: 총 {processed_count}권 처리 ---'))