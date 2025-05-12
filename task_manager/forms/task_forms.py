# task_manager/forms.py
from django import forms
from task_manager.models import Task

class TaskForm(forms.ModelForm):
    days_to_do = forms.CharField(required=False, help_text="Zilele sub formă de cifre separate prin virgulă: 1,2,3",
    widget=forms.TextInput(attrs={
        'placeholder': 'Zile pentru sarcini repetitive (1-7)',
        'class': 'input-field'
    })
)


    class Meta:
        model = Task
        fields = ['titlu', 'importanta', 'deadline', 'grup_task', 'repetitiv', 'days_to_do', 'def_time','data_completare']
        widgets = {
            'titlu': forms.TextInput(attrs={
                'class': 'input-field'
            }),
            'repetitiv': forms.CheckboxInput(attrs={
                'class': 'checkbox-field',
                'id': 'id_repetitiv'
            }),
            'importanta': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'input-field'
            }),
            'data_completare': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input-field'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input-field'
            }),
            'def_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'input-field'
            }),
        }

    def clean_days_to_do(self):
        data = self.cleaned_data.get('days_to_do','').strip()
        if not data:
            return None

        try:
            days = [int(x.strip()) for x in data.split(',') if x.strip()]
        except ValueError:
            raise forms.ValidationError('Zilele  trebuie sa fie numere intregi  separate prin virgula.')

        for day in days:
            if day < 1 or day > 7:
                raise forms.ValidationError('Zilele trebuie să fie între 1 și 7.')

        return days