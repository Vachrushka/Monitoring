from django import forms
from .models import Category, Exercise, Departament, AbsenceReason, Cadet


class SetCategoryForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                  empty_label=None,
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  label="Категория")
    class Meta:
        model = Category
        fields = ['category']


class SetExerciseForm(forms.ModelForm):
    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Упражнение"
    )
    class Meta:
        model = Exercise
        fields = ['exercise']

class SetDepartamentForm(forms.ModelForm):
    departament = forms.ModelChoiceField(
        queryset=Departament.objects.all(),
        required=True,
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Направление"
    )
    class Meta:
        model = Departament
        fields = ['departament']


class AbsenceForm(forms.ModelForm):
    class Meta:
        model = AbsenceReason
        fields = ['name']

class SetCadetResultForm(forms.ModelForm):
    class Meta:
        model = Cadet
        fields = ['name']  # Добавьте другие поля, если необходимо

    result = forms.FloatField()
