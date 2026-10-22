from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                "data-toggle": "password",
                "id": "password",
                "name": "password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password"]


class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                "data-toggle": "password",
                "id": "password",
                "name": "password",
                "minlength": "3"
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean_username(self):
        name = self.cleaned_data["username"]
        if User.objects.filter(username=name).exists():
            raise forms.ValidationError("This username is already taken.")
        return name

    def clean_password(self):
        from django.contrib.auth.password_validation import validate_password
        password = self.cleaned_data["password"]
        validate_password(password)
        return password
