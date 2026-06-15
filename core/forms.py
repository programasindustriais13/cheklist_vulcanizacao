from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Machine, ChecklistSession

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('specialty', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'specialty':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Prensa Vulcanizadora 01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição opcional da máquina...'}),
        }

class LeaderModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username

class ChecklistStartForm(forms.ModelForm):
    leader = LeaderModelChoiceField(
        queryset=User.objects.filter(specialty='Lider', is_active=True).order_by('first_name', 'username'),
        label='Líder de Turno',
        empty_label='Selecione o Líder de Turno',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = ChecklistSession
        fields = ['machine', 'leader']
        widgets = {
            'machine': forms.Select(attrs={'class': 'form-select'}),
        }
