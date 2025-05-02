# apps/authentication/adapters.py
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.first_name = request.data.get('first_name', '')
        user.last_name = request.data.get('last_name', '')
        if commit:
            user.save()
        return user

