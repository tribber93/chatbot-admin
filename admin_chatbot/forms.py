from django import forms
from django.contrib.auth.models import User
from django.forms import fields

from .models import FileUpload

class LoginForm(forms.Form):
    username = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Username'})
                )
    password = forms.CharField(
                    widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Password'})
                )

class UploadForm(forms.ModelForm):
    file_path = forms.FileField(label='Pilih file .pdf', 
                                widget=forms.ClearableFileInput(attrs={'class': 'form-control mt-3', 'accept': '.pdf'})
                                )# Tambahkan atribut accept untuk membatasi jenis file yang dapat diunggah
 
    class Meta:
        model = FileUpload
        fields = ['file_name', 'file_path']
        widgets = {
            'file_name': forms.HiddenInput(),  # Menyembunyikan field file_name
            
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Ambil nama file yang diunggah
        file_path = cleaned_data.get('file_path')
        if file_path:
            cleaned_data['file_name'] = file_path.name  # Set nilai file_name dengan nama file yang diunggah
        return cleaned_data