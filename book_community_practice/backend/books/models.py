from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    review_content = models.TextField()
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)

    description = models.TextField(verbose_name="책 소개", blank=True, null=True)
    isbn = models.CharField(max_length=13, verbose_name="ISBN", blank=True, null=True)
    cover = models.URLField(verbose_name="표지 이미지 URL", blank=True, null=True)
    publisher = models.CharField(max_length=100, verbose_name="출판사", blank=True, null=True)
    pub_date = models.DateField(verbose_name="출판일", blank=True, null=True)
    author_info = models.TextField(verbose_name="저자 정보", blank=True, null=True)
    author_photo = models.URLField(verbose_name="저자 사진 URL", blank=True, null=True)
    customer_review_rank = models.IntegerField(verbose_name="평점", default=0)
    subTitle = models.CharField(max_length=255, verbose_name="부제", blank=True, null=True)
    category = models.IntegerField(verbose_name="카테고리 ID", default=0)

    def __str__(self):
        return self.title
