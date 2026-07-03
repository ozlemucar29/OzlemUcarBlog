from django import forms
from django.contrib.auth.models import User
from .models import Post, Category, Profile

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Şifrenizi belirleyin...',
        'class': 'form-input'
    }), label="Şifre")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Şifrenizi tekrar girin...',
        'class': 'form-input'
    }), label="Şifre Tekrar")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Kullanıcı Adı',
            'email': 'E-posta',
            'first_name': 'Ad',
            'last_name': 'Soyad'
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Kullanıcı adı seçin...', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-posta adresinizi girin...', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Adınız...', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Soyadınız...', 'class': 'form-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten alınmış.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Şifreler eşleşmiyor.")
        return cleaned_data


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'summary', 'content', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Yazı başlığını girin...',
                'class': 'form-input'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'summary': forms.Textarea(attrs={
                'placeholder': 'Yazının kısa bir özetini yazın (kartlarda görünecek)...',
                'rows': 3,
                'class': 'form-textarea'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Blog yazınızın içeriğini buraya yazın...',
                'rows': 12,
                'class': 'form-textarea'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Adınız...', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Soyadınız...', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-posta adresiniz...', 'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'title', 'bio']
        labels = {
            'avatar': 'Profil Fotoğrafı',
            'title': 'Unvan / Meslek',
            'bio': 'Hakkımda'
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'title': forms.TextInput(attrs={'placeholder': 'Örn: Yazılım Geliştirici...', 'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Kendinizden kısaca bahsedin...', 'rows': 4, 'class': 'form-textarea'}),
        }
