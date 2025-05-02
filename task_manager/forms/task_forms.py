# task_manager/forms.py
from django import forms
from task_manager.models import Task

class TaskForm(forms.ModelForm):
    days_to_do = forms.CharField(required=False, help_text="Zilele sub formă de cifre separate prin virgulă: 1,2,3")

    class Meta:
        model = Task
        fields = ['titlu', 'importanta', 'deadline', 'grup_task', 'repetitiv', 'days_to_do', 'def_time']
        widgets = {
            'repetitiv': forms.CheckboxInput(attrs={'id': 'id_repetitiv'}),
            'importanta': forms.NumberInput(attrs={'min':1, 'max':5}),
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