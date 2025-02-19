from django import forms
from django.contrib.auth.forms import UserCreationForm

from conduit.profiles.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password1', 'password2')

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return confirm_password

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        print("# UserRegistrationForm.save() user: ", user)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
