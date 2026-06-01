import secrets
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.utils import timezone

from .forms import LoginForm, PasswordResetConfirmForm, PasswordResetEmailForm, SignUpForm, OTPVerificationForm
from .models import Profile, EmailOTP


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role=form.cleaned_data['role'])
            auth_login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('property_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('property_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, 'Logged in successfully.')
            return redirect('property_list')
    else:
        form = LoginForm(request)
    return render(request, 'registration/login.html', {'form': form})


def forgot_password(request):
    """
    Step 1: Ask for the registered email and generate/send a 6-digit OTP code.
    """
    if request.method == 'POST':
        form = PasswordResetEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                # Generate a secure 6-digit OTP code
                otp_code = str(secrets.SystemRandom().randint(100000, 999999))
                
                # Mark previous active OTPs for this user as verified/inactive to keep db clean
                EmailOTP.objects.filter(user=user, is_verified=False).update(is_verified=True)
                
                # Store OTP in the database
                EmailOTP.objects.create(user=user, otp=otp_code)
                
                # Store session keys for OTP step
                request.session['password_reset_user_id'] = user.pk
                request.session['password_reset_email'] = user.email
                request.session['otp_verified'] = False
                
                # Build plain text, trusted format email
                subject = "Your Verification Code - Smart Property Finder"
                message = (
                    f"Hello {user.username or 'Valued User'},\n\n"
                    f"We received a request to reset the password for your Smart Property Finder account.\n"
                    f"Your 6-digit verification code is:\n\n"
                    f"       {otp_code}\n\n"
                    f"This code is valid for exactly 5 minutes. If you did not request this, please ignore this email.\n\n"
                    f"Best regards,\n"
                    f"Security Team, Smart Property Finder"
                )
                
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=None,  # Will fallback to DEFAULT_FROM_EMAIL
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f'Verification code sent successfully to {user.email}.')
                    return redirect('verify_otp')
                except Exception as e:
                    messages.error(request, 'Unable to send verification email. Please check configuration.')
            else:
                messages.error(request, 'No active account found with that email address.')
    else:
        form = PasswordResetEmailForm()
    return render(request, 'registration/forgot_password.html', {'form': form})


def verify_otp(request):
    """
    Step 2: Collect the 6-digit OTP from the user and verify its validity.
    Supports resending code via a POST field 'resend'.
    """
    user_id = request.session.get('password_reset_user_id')
    email = request.session.get('password_reset_email')
    
    if not user_id or not email:
        messages.error(request, 'Session expired. Please request a new verification code.')
        return redirect('forgot_password')
        
    user = User.objects.filter(pk=user_id, is_active=True).first()
    if not user:
        messages.error(request, 'User account not found.')
        return redirect('forgot_password')

    # Handle resend request
    if request.method == 'POST' and request.POST.get('resend') == '1':
        otp_code = str(secrets.SystemRandom().randint(100000, 999999))
        EmailOTP.objects.filter(user=user, is_verified=False).update(is_verified=True)
        EmailOTP.objects.create(user=user, otp=otp_code)
        
        subject = "Your New Verification Code - Smart Property Finder"
        message = (
            f"Hello {user.username or 'Valued User'},\n\n"
            f"Here is your new 6-digit verification code:\n\n"
            f"       {otp_code}\n\n"
            f"This code will expire in 5 minutes.\n\n"
            f"Best regards,\n"
            f"Security Team, Smart Property Finder"
        )
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, f'A new verification code has been sent to {user.email}.')
        except Exception as e:
            messages.error(request, 'Could not resend code. Please try again.')
            
        return redirect('verify_otp')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            otp_record = EmailOTP.objects.filter(user=user, is_verified=False).order_by('-created_at').first()
            
            if otp_record and otp_record.otp == entered_otp:
                if otp_record.is_expired():
                    messages.error(request, 'This verification code has expired. Please click resend.')
                else:
                    otp_record.is_verified = True
                    otp_record.save()
                    request.session['otp_verified'] = True
                    messages.success(request, 'Identity verified successfully. Create your new password.')
                    return redirect('password_reset_confirm')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
    else:
        form = OTPVerificationForm()
        
    return render(request, 'registration/verify_otp.html', {
        'form': form,
        'email': email
    })


def password_reset_confirm(request):
    """
    Step 3: Allow the user to reset their password using secure hashing if identity is verified.
    """
    user_id = request.session.get('password_reset_user_id')
    otp_verified = request.session.get('otp_verified')
    
    if not user_id or not otp_verified:
        messages.error(request, 'You must verify your identity first.')
        return redirect('forgot_password')

    user = User.objects.filter(pk=user_id, is_active=True).first()
    if not user:
        request.session.pop('password_reset_user_id', None)
        request.session.pop('otp_verified', None)
        messages.error(request, 'Unable to locate user account.')
        return redirect('forgot_password')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(user, request.POST)
        if form.is_valid():
            # Secure password hashing is automatically done inside set_password
            user.set_password(form.cleaned_data['new_password1'])
            user.save(update_fields=['password'])
            
            # Clean up session state
            request.session.pop('password_reset_user_id', None)
            request.session.pop('password_reset_email', None)
            request.session.pop('otp_verified', None)
            
            messages.success(request, 'Password reset successful. Please log in.')
            return redirect('login')
    else:
        form = PasswordResetConfirmForm(user)
    return render(request, 'registration/reset_password.html', {'form': form})

