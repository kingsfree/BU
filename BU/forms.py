from django import forms
from BU.models import MyUser, Comments, Article

class LoginForm(forms.Form):
    '''
    登录Form
    '''
    # username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username", "required": "required", }),
    #                           max_length=50, error_messages={"required": "username不能为空", })
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "E-mail", "required": "required", }),
                             max_length=50, error_messages={"required": "Email不能为空", })
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password", "required": "required", }), max_length=20, error_messages={"required": "password不能为空", })

    def clean_email(self):
        email = self.cleaned_data['email']
        email_list = []
        users = MyUser.objects.all()
        for user in users:
            if user.email in email_list:
                pass
            else:
                email_list.append(user.email)
        if email not in email_list:
            raise forms.ValidationError('该邮箱没有在此站注册')
        else:
            return email



class RegForm(forms.ModelForm):
    '''
    注册表单
    '''
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "username,须介于4～20位之间", "required": "required", }), max_length=50, error_messages={"required": "username不能为空", })
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "Email", "required": "required", }),
                              max_length=50, error_messages={"required": "email不能为空", })

    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password,须介于6～16位之间", "required": "required", }), max_length=20, error_messages={"required": "password不能为空", })

    class Meta:
        model = MyUser
        fields = ('username', 'password', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        email_list = []
        users = MyUser.objects.all()
        for user in users:
            if user.email in email_list:
                pass
            else:
                email_list.append(user.email)
        if email in email_list:
            raise forms.ValidationError('该邮箱已注册！')
        else:
            return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 2 or len(username) > 16:
            raise forms.ValidationError('用户名须介于2～16位之间')
        users = MyUser.objects.all()
        username_list = []
        for user in users:
            if user.username in username_list:
                pass
            else:
                username_list.append(user.username)
        if username in username_list:
            raise forms.ValidationError('该用户名已注册')
        else:
            return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6 or len(password) > 16:
            raise forms.ValidationError('密码须介于6～16位之间')
        else:
            return password

class CommentForm(forms.ModelForm):
    '''
    评论表单
    '''
    content = forms.CharField(widget=forms.Textarea(attrs={"id": "comment", "required": "required",  "tabindex": "4", "class": "form-control", "name": "comment_content"}))  # , 'rows': '4', 'cols': '50'
    # article = forms.CharField(widget=forms.HiddenInput())


    class Meta:
        model = Comments
        fields = {'user', 'pid', 'article', 'content'}

class ResetPasswordForm(forms.Form):
    '''
    密码重置表单
    '''
    raw_code = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password", "required": "required", }), max_length=20, error_messages={"required": "password不能为空", })
    code = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Verify-Code", "required": "required", }), max_length=20, error_messages={"required": "password不能为空", })

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6 or len(password) > 16:
            raise forms.ValidationError('密码须介于6～16位之间')
        else:
            return password

    def clean_code(self):
        code = self.cleaned_data['code']
        if not len(code) == 6:
            raise forms.ValidationError('验证码必须为6位')
        else:
            return code




class EmailSendForm(forms.Form):
    '''
    发送验证码表单
    '''
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "E-mail", "required": "required", }), max_length=50, error_messages={"required": "Email不能为空", })

    def clean_email(self):
        email = self.cleaned_data['email']
        email_list = []
        users = MyUser.objects.all()
        for user in users:
            if user.email in email_list:
                pass
            else:
                email_list.append(user.email)
        if email not in email_list:
            raise forms.ValidationError('该邮箱没有在此站注册')
        else:
            return email


class AvatarForm(forms.ModelForm):

    class Meta:
        model = MyUser
        fields = {'avatar', 'username'}

class ArticlePubForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={"id": "title", "required": "required",  "tabindex": "1", "class": "form-control", "name": "title", 'placeholder': '标题不要超过50个字符'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={"id": "description", "required": "required", "tabindex": "2", "class": "form-control", "name": "description", 'placeholder': '摘要不要超过300个字符', 'rows': '3', }))
    content = forms.CharField(widget=forms.Textarea(
        attrs={"id": "article_content", "required": "required", "tabindex": "3", "class": "form-control",
               "name": "content", 'placeholder': '文章内容...', 'rows': '12'}))
    tagstext = forms.CharField(widget=forms.TextInput(
        attrs={"id": "article_tags", "required": "required",  "tabindex": "4", "class": "form-control", "name": "title", 'placeholder': '标签之间用‘,’（逗号）隔开'}))
    menu_category = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Article
        fields = {'title', 'description', 'content', 'photo'}

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise forms.ValidationError('标题不能超过50个字符')
        else:
            return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) > 300:
            raise forms.ValidationError('摘要不能超过300个字符')
        else:
            return description


class ArticleEditForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={"id": "title", "required": "required",  "tabindex": "1", "class": "form-control", "name": "title", 'placeholder': '标题不要超过50个字符'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={"id": "description", "required": "required", "tabindex": "2", "class": "form-control", "name": "description", 'placeholder': '摘要不要超过300个字符', 'rows': '3', }))
    content = forms.CharField(widget=forms.Textarea(
        attrs={"id": "article_content", "required": "required", "tabindex": "3", "class": "form-control",
               "name": "content", 'placeholder': '文章内容...', 'rows': '12'}))
    tagstext = forms.CharField(widget=forms.TextInput(
        attrs={"id": "article_tags", "required": "required",  "tabindex": "4", "class": "form-control", "name": "title", 'placeholder': '标签之间用‘,’（逗号）隔开'}))
    article_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Article
        fields = {'title', 'description', 'content', 'photo'}

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise forms.ValidationError('标题不能超过50个字符')
        else:
            return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) > 300:
            raise forms.ValidationError('摘要不能超过300个字符')
        else:
            return description

# class KeywordsForm(forms.Form):
#     keyword = forms.CharField(widget=forms.TextInput(
#         attrs={"id": "keywords", "required": "required",  "tabindex": "1", "class": "form-control", "name": "keywords", 'placeholder': 'Search', 'autocomplete': 'off'}), max_length=50, error_messages={"required": "关键字不能为空", })