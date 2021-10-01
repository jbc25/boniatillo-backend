# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.db.models import BLANK_CHOICE_DASH

from currency.models import Person
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator


class PersonForm(forms.ModelForm):
    # username_validators = [UnicodeUsernameValidator(), ASCIIUsernameValidator()]
    username_validators = []

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        form = super(PersonForm, self).__init__(*args, **kwargs)

    owner_id = forms.CharField(max_length=100, widget=forms.HiddenInput, required=False)
    is_new_person = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())
    new_user_username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, validators=username_validators)
    new_user_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    send_welcome_email = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'custom-control-input', 'checked': True}), required=False,
                                            label='Mandar email de bienvenida')

    class Meta:
        model = Person
        exclude = ['fav_entities', 'user']
        widgets = {
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', }),
            'surname': forms.TextInput(attrs={'class': 'form-control', }),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows':3,}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', }),
            'registered': forms.TextInput(attrs={'class': 'form-control', 'readonly':True}),
            'profile_image': forms.FileInput(attrs={}),
            'send_welcome_email': forms.CheckboxInput(attrs={'class':'custom-control-input', 'checked':True})
        }

    def clean_new_user_username(self):
        username = self.cleaned_data['new_user_username']
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            self.add_error('new_user_username', u'El nombre de usuario "%s" ya está en uso.' % username)
        return username


    def clean(self):
        cleaned_data = super(PersonForm, self).clean()

        is_new = cleaned_data.get('is_new_person')
        if is_new:
            owner_id = cleaned_data.get("owner_id")
            new_user_username = cleaned_data.get("new_user_username")
            new_user_password = cleaned_data.get("new_user_password")

            if owner_id or (new_user_password and new_user_username):
                return cleaned_data
            else:
                if new_user_username and not new_user_password:
                    self.add_error('owner_id', 'Introduce una contraseña')
                else:
                    self.add_error('owner_id', 'Selecciona un usuario asociado a la entidad o crea uno nuevo')