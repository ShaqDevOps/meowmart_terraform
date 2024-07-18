from django.conf import settings
from django import forms
from django.forms.widgets import DateInput
from us.states import STATES


class OrderForm(forms.Form):
    phone = forms.CharField(max_length=255, label='Phone Number')
    # birth_date = forms.DateField(
    #     required=False,
    #     widget=DateInput(attrs={'type': 'date'}),
    #     label='Birth Date'
    # )
    street = forms.CharField(max_length=255, label='Street Address')
    city = forms.CharField(max_length=255, label='City')
    state = forms.CharField(max_length=20, label='State')
    # Generate state choices dynamically
    STATE_CHOICES = [(state.abbr, state.name) for state in STATES]

    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        label='State',
        widget=forms.Select(attrs={
            'class': 'shadow appearance-none border rounded w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline custom-select'
        })
    )
