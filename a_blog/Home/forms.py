from django import forms

class PubBlogForm(forms.Form):
    title = forms.CharField(max_length=50,min_length=2,error_messages={
        'required': '请输入博客标题',
        'max_length': '博客标题长度不能大于50',
        'min_length': '博客标题长度不能小于2',
    })
    content = forms.CharField(min_length=2,error_messages={
        'required': '内容不能为空',
        'min_length': '博客长度不能小于2',
    })