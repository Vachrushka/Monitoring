from django import forms
from .models import Category, Exercise, Departament, AbsenceReason, Cadet, Uniforms
from datetime import date

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


class EditDepartamentForm(forms.ModelForm):
    class Meta:
        model = Departament
        fields = '__all__'
        labels = {
            "name": "Название",
            "platoon": "Взвод",
            "course": "Курс"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class EditCadetForm(forms.ModelForm):
    class Meta:
        model = Cadet
        fields = '__all__'
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "patronymic": "Отчество",
            "rank": "Звание",
            "departament": "Отделение",
            "course": "Курс"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class FilterForm(forms.Form):
    categories = Category.objects.all()

    # Создаем список кортежей в формате ('значение', 'отображаемое_название')
    category_choices = [(category.id, category.name) for category in categories]


    name = forms.CharField(required=True, label='ФИО',
                           widget=forms.TextInput(attrs={'class': 'form-control mr-2', 'placeholder': 'Начните вводить имя'}),
                           error_messages={'required': 'Пожалуйста, заполните поле "ФИО".'})
    discipline = forms.ChoiceField(
        choices=category_choices,
        label='Дисциплина',
        widget=forms.Select(attrs={'class': 'form-control mr-2'})
    )
    start_date = forms.DateField(label='Время (с)',
                                 widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mr-2'}))
    end_date = forms.DateField(label='Время (по)',
                               widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control mr-2'}))

