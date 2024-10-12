from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError, fields
from django.conf import settings

from .models import FileUpload

class LoginForm(forms.Form):
    username = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Username'})
                )
    password = forms.CharField(
                    widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Password'})
                )
class UploadForm(forms.ModelForm):
    ext = ", ".join(settings.ALLOWED_EXTENSIONS)
    file_path = forms.FileField(label='Pilih file', 
                                widget=forms.ClearableFileInput(attrs={'class': 'form-control mt-3', 'accept': ext}),
                                help_text=f'Maksimal ukuran file 3MB, format {ext}',
                                )# Tambahkan atribut accept untuk membatasi jenis file yang dapat diunggah
 
    class Meta:
        model = FileUpload
        fields = ['file_path']
    
    def clean(self):
        cleaned_data = super().clean()
        # Ambil nama file yang diunggah
        file_path = cleaned_data.get('file_path')
        if file_path:
            cleaned_data['file_name'] = file_path.name  # Set nilai file_name dengan nama file yang diunggah
        return cleaned_data
    
    # Supabase
    # def clean(self):
    #     cleaned_data = super().clean()
    #     # Ambil nama file yang diunggah
    #     file_path = cleaned_data.get('file_path')
    #     if file_path:
    #         cleaned_data['file_name'] = file_path.name  # Set nilai file_name dengan nama file yang diunggah
    #     return cleaned_data
    
class WhatsAppTokenForm(forms.Form):
    token_wa = forms.CharField(max_length=255, label='WhatsApp Token')