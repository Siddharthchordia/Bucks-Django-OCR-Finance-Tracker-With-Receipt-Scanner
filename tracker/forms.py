from django import forms
from tracker.models import Transaction,Category
from allauth.account.forms import SignupForm

class TransactionForm(forms.ModelForm):
    # noinspection PyTypeChecker
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget = forms.RadioSelect()
    )
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount<=0:
            raise forms.ValidationError("Amount must be positive number")
        else:
            return amount

    class Meta:
        model = Transaction
        fields = (
            'type',
            'amount',
            'date',
            'category',
        )
        widgets = {
            "date":forms.DateInput(attrs={'type':'date'})
        }

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user