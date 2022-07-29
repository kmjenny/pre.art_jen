from distutils.log import error
from socket import fromshare
from turtle import textinput
from django import forms
from .models import User, Authentication
from argon2 import PasswordHasher, exceptions

class SignupForm(forms.ModelForm):
    user_id = forms.CharField(
        label = '아이디',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class' : 'user-id',
                'placeholder' : '아이디'
            }
        ),
        error_messages={'required' : '아이디를 입력해주세요.',
                        'unique' : '중복된 아이디입니다.'}
    )

    pw = forms.CharField(
        label = '비밀번호',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class' : 'pw',
                'placeholder' : '비밀번호'
            }
        ),
        error_messages={'required' : '비밀번호를 입력해주세요.'}
    )

    pw_confirm = forms.CharField(
        label = '비밀번호 확인',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class' : 'pw_confirm',
                'placeholder' : '비밀번호 확인'
            }
        ),
        error_messages={'required' : '비밀번호가 일치하지 않습니다.'}
    )

    email = forms.EmailField(
        label = '이메일',
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class' : 'email',
                'placeholder' : '이메일'
            }
        ),
        error_messages={'required' : '이메일을 입력해주세요.'}
    )

    nickname = forms.CharField(
        label = '닉네임',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class' : 'nickname',
                'placeholder' : '닉네임'
            }
        ),
        error_messages={'required' : '닉네임을 입력해주세요.'}
    )

    birth = forms.DateField(
        label = '생년월일',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class' : 'birth',
                'placeholder' : '생년월일'
            }
        ),
        error_messages={'required' : '생년월일을 입력해주세요.'}
    )

    gender = forms.ChoiceField(
        label = '성별',
        required=True,
        choices = User.gender_choices,
        error_messages={'required' : '성별을 선택해주세요.'}
    )

    phone_number = forms.CharField(
        label = '전화번호',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class' : 'phone_number',
                'placeholder' : '전화번호'
            }
        ),
        error_messages={'required' : '전화번호를 입력해주세요.'}
    )

    field_order = [
        'user_id',
        'pw',
        'pw_confirm',
        'nickname',
        'email',
        'birth',
        'gender',
        'phone_number'
    ]

    class Meta:
        model = User
        fields = [
            'user_id',
            'pw',
            'nickname',
            'email',
            'birth',
            'gender',
            'phone_number'
        ]
    
    def clean(self):
        cleaned_data = super().clean()

        user_id = cleaned_data.get('user_id', '')
        pw = cleaned_data.get('pw', '')
        pw_confirm = cleaned_data.get('pw_confirm', '')
        nickname = cleaned_data.get('nickname', '')
        email = cleaned_data.get('email', '')
        birth = cleaned_data.get('birth', '')
        gender = cleaned_data.get('gender', '')
        phone_number = cleaned_data.get('phone_number', '')

        if pw != pw_confirm:
            return self.add_error('pw_confirm', '비밀번호가 다릅니다.')
        elif not (4<=len(user_id)<=16):
            return self.add_error('user_id', '아이디는 4~16자로 입력해주세요.')
        elif 8>len(pw):
            return self.add_error('pw', '비밀번호는 8자 이상으로 적어주세요.')
        else:
            self.user_id = user_id
            self.pw = PasswordHasher().hash(pw)
            self.pw_confirm = pw_confirm
            self.nickname = nickname
            self.email = email
            self.birth = birth
            self.gender = gender
            self.phone_number = phone_number

class LoginForm(forms.Form):
    user_id = forms.CharField(
        max_length=32,
        label = '아이디',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class' : 'user_id',
                'placeholder' : '아이디'
            }
        ),
        error_messages={'required' : '아이디를 입력해주세요.'}
    )
    pw = forms.CharField(
        max_length=128,
        label='비밀번호',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class' : 'pw',
                'placeholder' : '비밀번호'
            }
        ),
        error_messages={'required':'비밀번호를 입력해주세요.'}
    )

    field_order = [
        'user_id',
        'pw',
    ]

    def clean(self):
        cleaned_data = super().clean()

        user_id = cleaned_data.get('user_id', '')
        pw = cleaned_data.get('pw', '')

        if user_id == '':
            return self.add_error('user_id', '아이디를 다시 입력해주세요.')
        elif pw == '':
            return self.add_error('pw', '비밀번호를 다시 입력해주세요.')
        else:
            try:
                user=User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return self.add_error('user_id','존재하지 않는 아이디입니다.')

            try:
                PasswordHasher().verify(user.pw, pw)
            except exceptions.VerifyMismatchError:
                return self.add_error('pw', '비밀번호가 일치하지 않습니다.')
            
            self.login_session = user.user_id