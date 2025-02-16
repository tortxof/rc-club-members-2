from django import forms


class EmailReadOnlyTokenForm(forms.Form):
    email = forms.EmailField()
