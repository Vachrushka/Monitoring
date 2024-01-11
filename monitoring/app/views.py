import datetime
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.loader import render_to_string
from .forms import SetCategoryForm, SetExerciseForm, SetDepartamentForm, SetAbsenceForm, SetCadetResultForm, \
    SetUniformForm, EditDepartamentForm, EditCadetForm
from django.http import JsonResponse, HttpResponseBadRequest
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
def edit_users(request):
    return render(request, 'edit_users.html')


@login_required
def add_results(request):
    category_form = SetCategoryForm()
    exercise_form = SetExerciseForm()
    departament_form = SetDepartamentForm()
    set_result_form = SetCadetResultForm()
    absence_form = SetAbsenceForm()
    uniforms_form = SetUniformForm()

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
                absence_reason_id=item['absenceId'] if item['absenceId'] != '' else None,
                result=int(item['result']) if item['result'] != '' else None,
                datetime=pytz.timezone('UTC').localize(datetime.strptime(
                    f"{item['date']} {datetime.now().time().strftime('%H:%M:%S')}", "%Y-%m-%d %H:%M:%S"))
            )
        messages.success(request, 'Сохранение прошло успешно!')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, 'Произошла ошибка при сохранинии.')
        return JsonResponse({'success': False, 'error': str(e)})


# edit gr page
@login_required
def edit_groups(request):
    success = False
    if request.method == 'POST':
        form = EditDepartamentForm(request.POST)
        if form.is_valid():
            form.save()
            success = True

    context = {
        'departaments': Departament.objects.all().order_by('-id'),
        'form': EditDepartamentForm(),
        'success': success
    }
    return render(request, 'edit_groups.html', context)


@login_required
def update_group(request, pk):
    success_update = False
    get_group = get_object_or_404(Departament, pk=pk)
    if request.method == 'POST':
        form = EditDepartamentForm(request.POST, instance=get_group)
        if form.is_valid():
            form.save()
            success_update = True
        else:
            # Form is not valid, include it in the context for displaying errors
            context = {
                'get_group': get_group,
                'update': True,
                'form': form,  # Pass the form with errors to the context
                'success_update': success_update
            }
            return render(request, 'edit_groups.html', context)

    context = {
        'get_group': get_group,
        'update': True,
        'form': EditDepartamentForm(instance=get_group),
        'success_update': success_update
    }

    return render(request, 'edit_groups.html', context)



@login_required
def delete_group(request, pk):
    get_article = get_object_or_404(Departament, pk=pk)
    get_article.delete()

    return redirect('app:edit_groups')


# edit user page
@login_required
def edit_users(request):
    success = False
    search_term = request.GET.get('search', '')
    if request.method == 'POST':
        form = EditCadetForm(request.POST)
        if form.is_valid():
            form.save()
            success = True

    cadets = Cadet.objects.all().order_by('-id')
    if search_term:
        cadets = cadets.filter(name__icontains=search_term) | \
                 cadets.filter(surname__icontains=search_term) | \
                 cadets.filter(rank__name__icontains=search_term) | \
                 cadets.filter(departament__name__icontains=search_term) | \
                 cadets.filter(course__name__icontains=search_term) | \
                 cadets.filter(patronymic__icontains=search_term)

    context = {
        'departaments': cadets,
        'form': EditCadetForm(),
        'success': success
    }
    return render(request, 'edit_users.html', context)


@login_required
def update_user(request, pk):
    success_update = False
    get_group = get_object_or_404(Cadet, pk=pk)
    #get_group = Departament.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditCadetForm(request.POST, instance=get_group)
        if form.is_valid():
            form.save()
            success_update = True

    context = {
        'get_group': get_group,
        'update': True,
        'form': EditCadetForm(instance=get_group),
        'success_update': success_update
    }

    return render(request, 'edit_users.html', context)


@login_required
def delete_user(request, pk):
    get_article = get_object_or_404(Cadet, pk=pk)
    get_article.delete()

    return redirect('app:edit_users')


@login_required
def editing_page(request):
    return render(request, 'editing_page.html')


@login_required
def save_new_obj(request):
    form = None
    if request.method == 'POST':
        model_name = request.GET.get('model_name')
        if model_name == 'Cadet':
            form = EditCadetForm(request.POST)
        elif model_name == 'Departament':
            form = EditDepartamentForm(request.POST)

        try:
            if form and form.is_valid():
                form.save()
            else:
                raise Exception
        except Exception as e:
            return HttpResponseBadRequest

    context = {'success': True}
    return JsonResponse(context)
    # context = {
    #     'success': success
    # }
    # return render(request, 'editing_page.html', context)


@login_required
def get_editing_table(request):
    form = None
    headers = []
    data = []
    model_name = None
    # search_term = request.GET.get('search', '')
    if request.method == 'GET':
        model_name = request.GET.get('model_name')
        if model_name == 'Cadet':
            model_class = Cadet
            form = EditCadetForm()
            # data = model_class.objects.annotate(
            #     fio=Concat(
            #         F('surname'),
            #         Value(' '),
            #         F('name'),
            #         Value(' '),
            #         F('patronymic'),
            #         output_field=CharField()
            #     )
            # ).values('id', 'fio', 'rank__name', 'course__name', 'departament__name').order_by('-id')
            # headers = ['ID', 'ФИО', 'Звание', 'Курс', 'Отделение']
        elif model_name == 'Departament':
            model_class = Departament
            form = EditDepartamentForm()
            # data = model_class.objects.all().order_by('-id').values('id', 'name', 'platoon__name', 'course__name')
        else:
            return JsonResponse({"error": "Invalid model_name"})

        headers = [field.verbose_name for field in model_class._meta.fields]

        fields_to_include = []
        for field in model_class._meta.fields:
            fields_to_include.append(field.name if '_id' not in field.column else field.name + '__name')
        data = model_class.objects.all().order_by('-id').values(*fields_to_include)

    context = {
        'form': form,
        'headers': headers,
        'data': data,
        'model_name': model_name
    }
    return render(request, 'editing_page.html', context)

    # cadets = Cadet.objects.all().order_by('-id')
    # if search_term:
    #     cadets = cadets.filter(name__icontains=search_term) | \
    #              cadets.filter(surname__icontains=search_term) | \
    #              cadets.filter(rank__name__icontains=search_term) | \
    #              cadets.filter(departament__name__icontains=search_term) | \
    #              cadets.filter(course__name__icontains=search_term) | \
    #              cadets.filter(patronymic__icontains=search_term)
    #
    # returned_form = EditCadetForm

@login_required
def delete_object(request, obj, pk):
    model_class=None
    if obj == 'Cadet':
        model_class = Cadet
    elif obj == 'Departament':
        model_class = Departament
    get_article = get_object_or_404(model_class, pk=pk)
    get_article.delete()

    context = {
        'success_delete': True,
        'model_name': obj
    }
    return render(request, 'editing_page.html', context)

@login_required
def update_object(request, obj, pk):
    model_class = None
    form_model = None
    if obj == 'Cadet':
        model_class = Cadet
        form_model = EditCadetForm
    elif obj == 'Departament':
        model_class = Departament
        form_model = EditDepartamentForm
    success_update = False
    get_group = get_object_or_404(model_class, pk=pk)
    if request.method == 'POST':
        form = form_model(request.POST, instance=get_group)
        if form.is_valid():
            form.save()
            success_update = True

    if success_update:
        context = {
            'get_group': get_group,
            'form': form_model(instance=get_group),
            'success_update': success_update,
            'model_name': obj
        }
    else:
        context = {
            'get_group': get_group,
            'update': True,
            'form': form_model(instance=get_group),
            'success_update': success_update,
            'model_name': obj
        }

    return render(request, 'editing_page.html', context)
