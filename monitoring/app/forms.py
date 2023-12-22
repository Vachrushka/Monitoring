from django import forms
from .models import Category, Exercise


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
