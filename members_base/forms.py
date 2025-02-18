from django import forms


class EmailReadOnlyTokenForm(forms.Form):
    email = forms.EmailField()


class SendEmailForm(forms.Form):
    member_group = forms.ChoiceField(
        choices=(
            ("all", "All"),
            ("active", "Active"),
            ("current", "Current"),
            ("expired", "Expired"),
            ("previous", "Previous"),
        ),
    )
    from_email_user = forms.CharField()
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)
