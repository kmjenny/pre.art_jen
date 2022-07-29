from re import L
from django.shortcuts import render, redirect
from django.db import transaction
from .models import User
from argon2 import PasswordHasher
from .forms import SignupForm, LoginForm
# 전화번호 인증 부분(보류)
import json, requests, time, random
from django.views import View
from django.http import JsonResponse
from .utils import make_signature
from .models import Authentication

# Create your views here.
def signup(request):
    signup_form = SignupForm()
    context = {'forms' : signup_form}

    if request.method == 'GET':
        return render(request, 'accounts/signup.html', context)
    elif request.method == 'POST':
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            user = User(
                user_id = signup_form.user_id,
                pw = signup_form.pw,
                nickname = signup_form.nickname,
                email = signup_form.email,
                birth = signup_form.birth,
                gender = signup_form.gender,
                phone_number = signup_form.phone_number
            )
            user.save()
            return render(request, 'accounts/signup_done.html')
        else:
            context['forms'] = signup_form
            if signup_form.errors:
                for value in signup_form.errors.values():
                    context['error'] = value
        return render(request, 'accounts/signup.html', context)

def login(request):
    loginform = LoginForm()
    context = {'forms' : loginform}

    if request.method == 'GET':
        return render(request, 'accounts/login.html', context)
    elif request.method == 'POST':
        loginform = LoginForm(request.POST)

        if loginform.is_valid():
            request.session['login_session'] = loginform.login_session
            request.session.set_expiry(0)
            return redirect('main:showmain')
        else:
            context['forms']=loginform
            if loginform.errors:
                for value in loginform.errors.values():
                    context['error']=value
        return render(request, 'accounts/login.html', context)

def logout(request):
    request.session.flush()
    return redirect('main:showmain')

# 전화번호 인증 부분
class SmsSendView(View):
    def send_sms(self, phone_number, auth_number):
        timestamp = str(int(time.time() * 1000))  
        headers = {
            'Content-Type': "application/json; charset=UTF-8",
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': 'RBRMXDItYtF7hcR3kurm',
            'x-ncp-apigw-signature-v2': make_signature(timestamp)
        }
        body = {
            "type": "SMS", 
            "contentType": "COMM",
            "from": "01034002891",
            "content": f"[Pre.Art] 인증번호 [{auth_number}]를 입력해주세요.",
            "messages": [{"to": f"{phone_number}"}]
        }
        body = json.dumps(body)
        url = 'https://sens.apigw.ntruss.com/sms/v2/services/ncp:sms:kr:289537147905:pre_art/messages'
        requests.post(url, headers=headers, data=body)
        
    def post(self, request):
        data = json.loads(request.body)
        try:
            input_mobile_num = data['phone_number']
            auth_num = random.randint(10000, 100000)
            auth_mobile = Authentication.objects.get(phone_number=input_mobile_num)
            auth_mobile.auth_number = auth_num
            auth_mobile.save()
            self.send_sms(phone_number=data['phone_number'], auth_number=auth_num)
            return JsonResponse({'message': '인증번호 발송완료'}, status=200)
        except Authentication.DoesNotExist:
            Authentication.objects.create(
                phone_number=input_mobile_num,
                auth_number=auth_num,
            ).save()
            self.send_sms(phone_number=input_mobile_num, auth_number=auth_num)
            return JsonResponse({'message': '인증번호 발송 및 DB 입력완료'}, status=200)

# 네이버 SMS 인증번호 검증
class SMSVerificationView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            verification = Authentication.objects.get(phone_number=data['phone_number'])

            if verification.auth_number == data['auth_number']:
                return JsonResponse({'message': '인증 완료되었습니다.'}, status=200)

            else:
                return JsonResponse({'message': '인증 실패입니다.'}, status=400)

        except Authentication.DoesNotExist:
            return JsonResponse({'message': '해당 휴대폰 번호가 존재하지 않습니다.'}, status=400)