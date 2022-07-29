from email import header
from msilib import gen_uuid
from django.db import models
#핸드폰 인증 부분
from random import randint
from django.db import models

# Create your models here.
class User(models.Model):
    gender_choices = [
        ('선택', None),
        ('남성', '남성'),
        ('여성', '여성'),
    ]
    user_id = models.CharField(max_length=32, unique=True, verbose_name='아이디')
    pw = models.CharField(max_length=128, verbose_name='비밀번호')
    nickname = models.CharField(max_length=16, unique=True, verbose_name='닉네임')
    email = models.EmailField(max_length=128, unique=True, verbose_name='이메일')
    phone_number = models.CharField(max_length = 30, null=True, unique=True, verbose_name='전화번호')
    birth = models.DateField(max_length=20, verbose_name='생년월일')
    gender = models.CharField(max_length=5, choices = gender_choices, default = '선택', verbose_name='성별')

    def __str__(self):
        return self.nickname

    class Meta:
        db_table = 'user'
        verbose_name = '유저'
        verbose_name_plural = '유저'

# 핸드폰 인증
class Authentication(models.Model):
    phone_number = models.CharField(verbose_name='전화번호', primary_key=True, max_length=11)
    auth_number = models.IntegerField(verbose_name='인증번호')

    class Meta:
        db_table = 'authentications'
        verbose_name_plural = "휴대폰 인증 관리 페이지"