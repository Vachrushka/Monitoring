from django import forms
from .models import Category, Exercise, Departament, AbsenceReason, Cadet, Uniforms


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


class SetAbsenceForm(forms.ModelForm):
    absence = forms.ModelChoiceField(
        queryset=AbsenceReason.objects.all(),
        empty_label='',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Причина отсутствия",
        required=False)

    class Meta:
        model = AbsenceReason
        fields = ['absence']

class SetCadetResultForm(forms.ModelForm):
    class Meta:
        model = Cadet
        fields = ['name']

    result = forms.FloatField()

class SetUniformForm(forms.ModelForm):
    uniforms = forms.ModelChoiceField(
        queryset=Uniforms.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Тип формы",
        required=False)

    class Meta:
        model = Uniforms
        fields = ['uniforms']
