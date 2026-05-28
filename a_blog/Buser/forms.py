from django import forms

# 注册表单
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=15,min_length=1,error_messages={
        'required': '请输入昵称',
        'max_length': '用户名不能大于15',
        'min_length': '用户名不能小于1',
    })
    email = forms.EmailField(error_messages={
        'required': '请输入邮箱',
        'invalid': '请输入一个正确的邮箱'
    })
    password = forms.CharField(max_length=20,min_length=8,error_messages={
        'required': '请输入密码',
        'max_length': '密码不能大于15',
        'min_length': '密码不能小于8',
    })

# 登录表单
class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={
        'required': '请输入邮箱',
        'invalid': '请输入一个正确的邮箱'
    })
    password = forms.CharField(max_length=20,min_length=8,error_messages={
        'required': '请输入密码',
        'max_length': '密码不能大于15',
        'min_length': '密码不能小于8',
    })
    #                             非必填，由于前端传入False，后端判断没有字段，所以出此下策
    remember = forms.BooleanField(required=False)
    