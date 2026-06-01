from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or email')

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username or email',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            login_identifier = username.strip()
            if '@' in login_identifier:
                user = User.objects.filter(email__iexact=login_identifier, is_active=True).first()
                login_identifier = user.get_username() if user else login_identifier

            self.user_cache = authenticate(
                self.request,
                username=login_identifier,
                password=password,
            )
            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(label='Email address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
            'autocomplete': 'email',
        })

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError('Enter the email address registered with your account.')
        return email


class PasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class OTPVerificationForm(forms.Form):
    """
    Form to verify the 6-digit OTP received via email.
    """
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fs-2 py-2',
            'placeholder': '• • • • • •',
            'autocomplete': 'one-time-code',
            'style': 'letter-spacing: 0.5rem; font-weight: bold; color: #c9a14a; background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.15);'
        }),
        label="6-Digit Verification Code"
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp', '').strip()
        if not otp:
            raise forms.ValidationError("Please enter the code.")
        if not otp.isdigit():
            raise forms.ValidationError("Verification code must contain only numbers.")
        if len(otp) != 6:
            raise forms.ValidationError("Verification code must be exactly 6 digits.")
        return otp

