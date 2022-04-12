from django import forms


class DateForm(forms.Form):
    dateTo = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'name':'date_to',
            'type' : 'date'

        })
    )
    dateFrom = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'name': 'date_from',
            'type': 'date'
        })
    )