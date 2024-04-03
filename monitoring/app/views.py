from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.loader import render_to_string
from .forms import SetCategoryForm, SetExerciseForm, SetDepartamentForm, SetAbsenceForm, SetCadetResultForm, \
    SetUniformForm, EditDepartamentForm, EditCadetForm, FilterForm, EditPlatoonForm, EditCompanyForm, EditFacultyForm, \
    FilterFormLoadFile
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .models import Exercise, ExerciseStandard, Departament, Cadet, Uniforms, Grading, Category,\
    Course, Faculty,Company,Platoon,LeaderData
from django.http import JsonResponse
from django.views import View
from django import forms
import logging
import json
from datetime import datetime, timedelta
import pytz
from .utils import calculate_points, get_excel_io

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html', {'user_authenticated': request.user.is_authenticated})


def control(request):
    if 'term' in request.GET:
        search_term = request.GET.get('term', '')
        # cadets = Cadet.objects.filter(name__icontains=term).values('id', 'name', 'surname', 'patronymic')
        cadets = Cadet.objects.all().order_by('-id')
        cadets_f = cadets.filter(name__icontains=search_term) | \
                   cadets.filter(surname__icontains=search_term) | \
                   cadets.filter(rank__name__icontains=search_term) | \
                   cadets.filter(departament__name__icontains=search_term) | \
                   cadets.filter(course__name__icontains=search_term) | \
                   cadets.filter(patronymic__icontains=search_term)
        suggestions = []
        for cadet in cadets_f:
            full_name = f"{cadet.surname} {cadet.name} {cadet.patronymic}"
            # full_name = f"{cadet['surname']} {cadet['name']} {cadet['patronymic']}"
            suggestions.append({'id': cadet.pk, 'value': cadet.pk, 'label': full_name})
        return JsonResponse(suggestions, safe=False)

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            # Обработка данных формы
            name = form.cleaned_data['name']
            cadet_pk = request.POST.get('name_hidden')
            category_pk = form.cleaned_data['discipline']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            student = None
            if cadet_pk != '':
                student = get_object_or_404(Cadet, pk=cadet_pk)
            else:
                name_parts = name.split()
                if len(name_parts) == 3:
                    surname, name, patronymic = name_parts
                    try:
                    # Используем запрос к базе данных для поиска студента
                        student = Cadet.objects.get(name=name, surname=surname, patronymic=patronymic)
                    except Cadet.DoesNotExist:
                        context = {
                            'user_authenticated': request.user.is_authenticated,
                            'form': form,
                            'discipline': category_pk,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        return render(request, 'control.html', context)

            end_date += timedelta(days=1)

            queryset = Grading.objects.filter(
                student=student,
                datetime__gte=start_date,
                datetime__lte=end_date
            )
            grading_data = queryset.values().order_by('datetime')

            category = get_object_or_404(Category, pk=category_pk)
            related_exercises = Exercise.objects.filter(category=category)
            unform_types = Uniforms.objects.all().order_by('-id')

            datas = []
            for exercise in related_exercises:
                table_data = {}
                table_data['exercise_name'] = exercise.name
                exercise_notes = grading_data.filter(exercise__pk=exercise.pk)

                data = []
                for uniform in unform_types:
                    uniform_data = {}
                    uniform_data['uniform_name'] = uniform.name
                    uniform_data['data'] = []
                    # uniform_data['x'] = []
                    # uniform_data['y'] = []
                    uniform_notes = exercise_notes.filter(uniform_type__pk=uniform.pk)
                    for entry in uniform_notes:
                        if entry['result']:
                            uniform_data['data'].append({'x': entry['datetime'].isoformat(), 'y': int(entry['result'])})
                            # uniform_data['x'].append(entry['datetime'].date())
                            # uniform_data['y'].append(int(entry['result']))

                    data.append(uniform_data)

                #data, labels = get_filled_data(data)
                #table_data['labels'] = labels
                table_data['data'] = data

                datas.append(table_data)


            # После обработки данных, вы можете передать их в контекст шаблона
            context = {
                'user_authenticated': request.user.is_authenticated,
                'form': form,
                'name': name,
                'discipline': category_pk,
                'start_date': start_date,
                'end_date': end_date,
                'name_hidden': cadet_pk,
                'datas': datas,
            }
            return render(request, 'control.html', context)
    else:
        form = FilterForm()
    return render(request, 'control.html', {'user_authenticated': request.user.is_authenticated, 'form': form})


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

    return render(request, 'login.html', {'user_authenticated': request.user.is_authenticated})


# def user_logout(request):
#     logout(request)
#     messages.info(request, 'Вы успешно вышли из системы.')
#     return redirect('home')

@login_required
def test_page(request):
    context = {}
    context['data'] = ['1', '2', '3']
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
    # 3-5 курсы имеют норматив 3-го курса
    cource = departament.course if int(departament.course.name) <= 3 else get_object_or_404(Course, name='3')
    exercise_standart = ExerciseStandard.objects.filter(
        exercise=exercise,
        course=cource,
        uniform_type=uniform
    ).first()

    # Проверка наличия записи
    if exercise_standart:
        # Возвращение данных в формате JSON
        return JsonResponse({
            'value_satisfactory': exercise_standart.value_satisfactory,
            'value_fine': exercise_standart.value_fine,
            'value_great': exercise_standart.value_great,
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

import threading
from django.shortcuts import render
import time

lock = threading.Lock()
def update_leadtable_task():
    logger.info('update_leadtable_task started')

    old_leaders = LeaderData.objects.all()  # old rate, прирост
    LeaderData.objects.all().delete()
    # сформировать новую таблицу
    models = [Departament, Platoon, Company, Faculty]

    # рейтинг - сумма по всем дисциплинам
    # берем сумму последних рейтинг по ним для каждого кадета
    excercises = Exercise.objects.all()
    form_type = Uniforms.objects.all()

    content_type = ContentType.objects.get_for_model(Cadet)
    new_result_cadets = []
    for cadet in Cadet.objects.all():
        summary_rate = 0
        delta = 0
        for ex in excercises:
            for form in form_type:
                latest_grading = Grading.objects.filter(uniform_type=form.id, student_id=cadet.id, exercise_id=ex.id, rate__isnull=False).order_by('-datetime')[:2]
                if len(latest_grading) == 1:
                    summary_rate += latest_grading[0].rate
                elif len(latest_grading) == 2:
                    summary_rate += latest_grading[0].rate
                    delta += latest_grading[0].rate - latest_grading[1].rate

        res = LeaderData.objects.create(content_type=content_type, object_id=cadet.pk,
                                  leader_object=cadet, position_delta=delta,
                                  rate=summary_rate)
        new_result_cadets.append(res)
        res.save()

    def get_rates(object, o_l):
        cls = type(object)
        content_type = ContentType.objects.get_for_model(cls)

        old_rate = 0
        for lead in o_l:
            if lead.content_type == content_type and lead.object_id == object.pk:
                old_rate = lead.rate if lead.rate else 0

        # подсчет нового
        summary_rate = 0
        # получить все объекты нижнего в иерархии объекта, ссылаемого на этот объект
        if cls is Departament:
            # получить grades всех кадетов
            cads_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Cadet))
            # фильтруем - оставляем тех, у кого такой же dep
            dep_cadets = Cadet.objects.filter(departament=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            for c_gr in cads_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)

            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
        elif cls is Platoon:
            dep_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Departament))
            dep_cadets = Departament.objects.filter(platoon=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            for c_gr in dep_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
        elif cls is Company:
            comp_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Platoon))
            dep_cadets = Platoon.objects.filter(company=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            for c_gr in comp_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
        elif cls is Faculty:
            facl_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Company))
            dep_cadets = Company.objects.filter(faculty=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            for c_gr in facl_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])

        return old_rate, summary_rate

    def get_rates_2(object):
        cls = type(object)
        # подсчет нового
        summary_rate = 0
        delta = 0
        # получить все объекты нижнего в иерархии объекта, ссылаемого на этот объект
        if cls is Departament:
            # получить grades всех кадетов
            cads_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Cadet))
            # фильтруем - оставляем тех, у кого такой же dep
            dep_cadets = Cadet.objects.filter(departament=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            delta_gr = []
            for c_gr in cads_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
                    delta_gr.append(c_gr.position_delta)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
            delta = sum([gr for gr in delta_gr])
        elif cls is Platoon:
            dep_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Departament))
            dep_cadets = Departament.objects.filter(platoon=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            delta_gr = []
            for c_gr in dep_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
                    delta_gr.append(c_gr.position_delta)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
            delta = sum([gr for gr in delta_gr])
        elif cls is Company:
            comp_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Platoon))
            dep_cadets = Platoon.objects.filter(company=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            delta_gr = []
            for c_gr in comp_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
                    delta_gr.append(c_gr.position_delta)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
            delta = sum([gr for gr in delta_gr])
        elif cls is Faculty:
            facl_grades = LeaderData.objects.filter(content_type=ContentType.objects.get_for_model(Company))
            dep_cadets = Company.objects.filter(faculty=object)
            ids = [cad.pk for cad in dep_cadets]
            sum_gr = []
            delta_gr = []
            for c_gr in facl_grades[:]:
                if c_gr.object_id in ids:
                    sum_gr.append(c_gr.rate)
                    delta_gr.append(c_gr.position_delta)
            # просуммировать
            summary_rate = sum([gr for gr in sum_gr])
            delta = sum([gr for gr in delta_gr])

        return delta, summary_rate

    for model in models:
        # получить все данные таблицs
        model_data = model.objects.all()
        content_type = ContentType.objects.get_for_model(model)
        for obj in model_data:
            delta, summary_rate = get_rates_2(obj)
            # old_rate, summary_rate = get_rates(obj, old_leaders)
            LeaderData.objects.create(content_type=content_type, object_id=obj.pk,
                                      leader_object=obj, position_delta=delta, rate=summary_rate).save()


    logger.info('update_leadtable_task end')


@login_required
@require_POST
def save_grading_data(request):
    try:
        # Получаем данные из POST-запроса
        data = json.loads(request.body)
        cadets = list(Cadet.objects.filter(departament_id=data['departamentId']).values('id'))
        exercise_id = data['exerciseId']
        uniform_type_id = data['uniformId']
        course_id = Cadet.objects.get(id=cadets[0]['id']).course_id
        exercise_standard = get_object_or_404(ExerciseStandard, course=course_id, exercise=exercise_id, uniform_type=uniform_type_id)
        # Проходим по всем данным и сохраняем их в базу данных
        for ind, item in enumerate(data['results']):
            rate = None
            if item['result'] != '':
                rate = calculate_points(int(item['result']), exercise_standard.value_satisfactory,
                                        exercise_standard.value_great, exercise_standard.koef_down_great,
                                        exercise_standard.koef_up_great, exercise_standard.reverse)
            Grading.objects.create(
                student_id=cadets[ind]['id'],
                exercise_id=exercise_id,
                uniform_type_id=uniform_type_id,
                absence_reason_id=item['absenceId'] if item['absenceId'] != '' else None,
                result=int(item['result']) if item['result'] != '' else None,
                datetime=pytz.timezone('UTC').localize(datetime.strptime(
                    f"{item['date']} {datetime.now().time().strftime('%H:%M:%S')}", "%Y-%m-%d %H:%M:%S")),
                rate=rate
            )
        messages.success(request, 'Сохранение прошло успешно!')
        # запуск задачи на обновление таблицы лидеров
        if not lock.locked():
            # Блокируем задачу
            with lock:
                # Запуск задачи в фоне
                background_thread = threading.Thread(target=update_leadtable_task)
                background_thread.start()
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f'Произошла ошибка при сохранинии. {e}')
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

# edit learn subjects

# platoons
@login_required
def edit_platoons(request):
    success = False
    if request.method == 'POST':
        form = EditPlatoonForm(request.POST)
        if form.is_valid():
            form.save()
            success = True

    context = {
        'departaments': Platoon.objects.all().order_by('-id'),
        'form': EditPlatoonForm(),
        'success': success
    }
    return render(request, 'edit_platoons.html', context)


@login_required
def update_platoon(request, pk):
    success_update = False
    get_group = get_object_or_404(Platoon, pk=pk)
    if request.method == 'POST':
        form = EditPlatoonForm(request.POST, instance=get_group)
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
            return render(request, 'edit_platoons.html', context)

    context = {
        'get_group': get_group,
        'update': True,
        'form': EditPlatoonForm(instance=get_group),
        'success_update': success_update
    }

    return render(request, 'edit_platoons.html', context)


@login_required
def delete_platoon(request, pk):
    get_article = get_object_or_404(Platoon, pk=pk)
    get_article.delete()

    return redirect('app:edit_platoons')


# companies
@login_required
def edit_companies(request):
    success = False
    if request.method == 'POST':
        form = EditCompanyForm(request.POST)
        if form.is_valid():
            form.save()
            success = True

    context = {
        'departaments': Company.objects.all().order_by('-id'),
        'form': EditCompanyForm(),
        'success': success
    }
    return render(request, 'edit_companies.html', context)


@login_required
def update_company(request, pk):
    success_update = False
    get_group = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = EditCompanyForm(request.POST, instance=get_group)
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
            return render(request, 'edit_companies.html', context)

    context = {
        'get_group': get_group,
        'update': True,
        'form': EditCompanyForm(instance=get_group),
        'success_update': success_update
    }

    return render(request, 'edit_companies.html', context)


@login_required
def delete_company(request, pk):
    get_article = get_object_or_404(Company, pk=pk)
    get_article.delete()

    return redirect('app:edit_companies')


# faculty
@login_required
def edit_faculty(request):
    success = False
    if request.method == 'POST':
        form = EditFacultyForm(request.POST)
        if form.is_valid():
            form.save()
            success = True

    context = {
        'departaments': Faculty.objects.all().order_by('-id'),
        'form': EditFacultyForm(),
        'success': success
    }
    return render(request, 'edit_faculty.html', context)


@login_required
def update_faculty(request, pk):
    success_update = False
    get_group = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        form = EditFacultyForm(request.POST, instance=get_group)
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
            return render(request, 'edit_faculty.html', context)

    context = {
        'get_group': get_group,
        'update': True,
        'form': EditFacultyForm(instance=get_group),
        'success_update': success_update
    }

    return render(request, 'edit_faculty.html', context)


@login_required
def delete_faculty(request, pk):
    get_article = get_object_or_404(Faculty, pk=pk)
    get_article.delete()

    return redirect('app:edit_faculty')



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


def handle_uploaded_file(f):
    with open(f'media/profile_pics/f.name', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def update_user(request, pk):
    success_update = False
    get_group = get_object_or_404(Cadet, pk=pk)
    if request.method == 'POST':
        form = EditCadetForm(request.POST, request.FILES, instance=get_group)
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
    model_class = None
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

def get_name(grade, model):
    return str(model.objects.get(pk=grade.object_id))

def get_top_10(model):
    content_type = ContentType.objects.get_for_model(model)
    top_10_records = LeaderData.objects.order_by('-position_delta').filter(content_type=content_type)[:10]
    data = []
    pks = []
    i = 1
    for note in top_10_records:
        data.append([i, note.position_delta, note.rate, get_name(note, model)])
        pks.append(note.object_id)
        i += 1
    return data, pks

def get_leaderboards(request):
    cadets, pks = get_top_10(Cadet)
    f, _ = get_top_10(Faculty)
    c, _ = get_top_10(Company)
    p, _ = get_top_10(Platoon)
    d, _ = get_top_10(Departament)
    data = {
        "table-fcl": f,
        "table-cmp": c,
        "table-plt": p,
        "table-dep": d,
        "table-cadet": cadets,
        "cadets_pk": pks
    }
    return JsonResponse(data)


def get_user_data(request, pk):
    user_data = get_object_or_404(Cadet, pk=pk)
    if not str(user_data.photo):
        path = "static/img/author.jpg"
    elif "static" not in str(user_data.photo):
        path = 'media/' + str(user_data.photo)
    else:
        path = str(user_data.photo)

    data = {
        'full_name': str(user_data),
        'rank': str(user_data.rank),
        'departament': str(user_data.departament),
        'course': str(user_data.course),
        'photo_url': path
    }
    return JsonResponse(data)


from django.http import HttpResponse
from urllib.parse import quote

def get_grade_data(student, category_pk, start_date, end_date):
    if category_pk == 'all':
        categories = Category.objects.all()
    else:
        categories = [get_object_or_404(Category, pk=category_pk)]

    result = {}
    for cat in categories:
        exercises = Exercise.objects.filter(category_id=cat.id)

        excercise_dict = {}
        for ex in exercises:
            grades = Grading.objects.filter(student=student.id, exercise=ex.id,
                                            datetime__gte=start_date,
                                            datetime__lte=end_date)
            excercise_dict[ex] = grades
        result[cat] = excercise_dict

    return result
@login_required
def report(request):
    if request.method == 'POST':
        form = FilterFormLoadFile(request.POST)
        # обработка
        if form.is_valid():
            # Обработка данных формы
            name = form.cleaned_data['name']
            cadet_pk = request.POST.get('name_hidden')
            category_pk = form.cleaned_data['discipline']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            student = None
            if cadet_pk != '':
                student = get_object_or_404(Cadet, pk=cadet_pk)

            data = get_grade_data(student, category_pk, start_date, end_date)
            excel_io = get_excel_io(student, start_date, end_date, data)
            response = HttpResponse(excel_io.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = quote(f"Отчет: {name} - {str(start_date)} - {str(end_date)}.xlsx")
            response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
            return response
    else:
        form = FilterFormLoadFile()


    return render(request, 'report.html', {'user_authenticated': request.user.is_authenticated, 'form': form})

