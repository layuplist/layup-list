from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from web.models import Student


class SignupForm(forms.Form):
    """
    modified from UserCreationForm:
    https://github.com/django/django/blob/master/django/contrib/auth/forms.py
    """

    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }

    email = forms.EmailField(label="Dartmouth Undergraduate Email")
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification.")

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        email = self.cleaned_data.get("email")
        validate_password(password1, User(username=email, email=email))
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        username = email.split("@")[0]

        if not Student.objects.is_valid_dartmouth_student_email(email):
            raise ValidationError(
                "Only Dartmouth student emails are permitted for registration"
                " at this time.")

        if len(username) > 30:
            raise ValidationError("Please use a shorter email.")

        if User.objects.filter(Q(username=username) | Q(email=email)):
            raise ValidationError("A user with that email already exists")

        return email

    @transaction.atomic()
    def save_and_send_confirmation(self, request):
        new_user = User.objects.create_user(
            username=self.cleaned_data["email"].split("@")[0],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            is_active=False
        )

        new_student = Student.objects.create(
            user=new_user,
            confirmation_link=User.objects.make_random_password(length=16)
        )
        new_student.send_confirmation_link(request)

        return new_user
