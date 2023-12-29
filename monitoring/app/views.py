import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SetCategoryForm, SetExerciseForm, SetDepartamentForm, SetAbsenceForm, SetCadetResultForm, SetUniformForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Exercise, ExerciseStandard, Departament, Cadet, Uniforms, Grading
from django.http import JsonResponse
from django.views import View
from django import forms
import logging
import json
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html', {'user_authenticated': request.user.is_authenticated})


def control(request):
    return render(request, 'control.html', {'user_authenticated': request.user.is_authenticated})


def author(request):
    return render(request, 'author.html', {'user_authenticated': request.user.is_authenticated})


# def login_view(request):
#     return render(request, 'login.html', {'user_authenticated': request.user.is_authenticated})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему.')
            return redirect('app:index')
        else:
            messages.error(request, 'Неверный логин или пароль.')

    return render(request, 'login.html',  {'user_authenticated': request.user.is_authenticated})


# def user_logout(request):
#     logout(request)
#     messages.info(request, 'Вы успешно вышли из системы.')
#     return redirect('home')

@login_required
def test_page(request):
    context = {}
    context['data'] = ['1','2','3']
    return render(request, 'test_page.html', context)

@login_required
def editing(request):
    return render(request, 'editing.html')


@login_required
def add_results(request):
    category_form = SetCategoryForm()
    exercise_form = SetExerciseForm()
    departament_form = SetDepartamentForm()
    set_result_form = SetCadetResultForm()
    absence_form = SetAbsenceForm()
    uniforms_form = SetUniformForm()

    if request.method == 'POST':
        category_form = SetCategoryForm(request.POST)
        exercise_form = SetExerciseForm(request.POST)

        if category_form.is_valid() and exercise_form.is_valid():
            # Делайте что-то с выбранными данными
            category_name = category_form.cleaned_data['name']
            exercise_name = exercise_form.cleaned_data['name']
            # ...

    return render(request, 'add_results.html',
                  {'category_form': category_form,
                   'exercise_form': exercise_form,
                   'departament_form': departament_form,
                   'set_result_form': set_result_form,
                   'absence_form': absence_form,
                   'uniforms_form': uniforms_form,
                   })

@login_required
def get_exercises_for_category(request, category_id):
    exercises = Exercise.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'exercises': list(exercises)})


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

@login_required
def get_exercise_standard(request, exercise_id, departament_id, uniform_id):
    # Получение объекта Exercise
    exercise = get_object_or_404(Exercise, pk=exercise_id)

    # Получение объекта Departament
    departament = get_object_or_404(Departament, pk=departament_id)
    uniform = get_object_or_404(Uniforms, pk=uniform_id)
    # Получение соответствующего ExerciseStandard
    exercise_standart = ExerciseStandard.objects.filter(
        exercise=exercise,
        course=departament.course,
        uniform_type=uniform
    ).first()

    # Проверка наличия записи
    if exercise_standart:
        # Возвращение данных в формате JSON
        return JsonResponse({
            'value': exercise_standart.value,
            'description': exercise_standart.description,
            # Другие поля exercise_standart
        })
    else:
        # Если запись не найдена
        return JsonResponse({
            'value': None,
            'description': None
        })


@login_required
def get_cadets_from_dep(request, departament_id):
    cadets = Cadet.objects.filter(departament_id=departament_id).values('id', 'name', "surname", "patronymic")
    return JsonResponse({'exercises': list(cadets)})


@login_required
@require_POST
def save_grading_data(request):
    try:
        # Получаем данные из POST-запроса
        data = json.loads(request.body)
        cadets = list(Cadet.objects.filter(departament_id=data['departamentId']).values('id'))
        exercise_id = data['exerciseId']
        uniform_type_id = data['uniformId']
        # Проходим по всем данным и сохраняем их в базу данных
        for ind, item in enumerate(data['results']):
            Grading.objects.create(
                student_id=cadets[ind]['id'],
                exercise_id=exercise_id,
                uniform_type_id=uniform_type_id,
                absence_reason_id=item['absenceId'] if item['absenceId'] is not '' else None,
                result=int(item['result']) if item['result'] is not '' else None,
                datetime=pytz.timezone('UTC').localize(datetime.strptime(
                    f"{item['date']} {datetime.now().time().strftime('%H:%M:%S')}", "%Y-%m-%d %H:%M:%S"))
            )
        messages.success(request, 'Сохранение прошло успешно!')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, 'Произошла ошибка при сохранинии.')
        return JsonResponse({'success': False, 'error': str(e)})
