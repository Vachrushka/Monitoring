from django.contrib import admin
from .models import Faculty, Company, Platoon, Departament
from .models import Course, Rank, Cadet
from .models import Category, Exercise, ExerciseStandard, AbsenceReason, Grading, Uniforms, CadetProfile


# Получение всех моделей из текущего приложения
app_models = [Faculty, Company, Platoon, Category, Exercise,
              ExerciseStandard, AbsenceReason, Grading, Uniforms, CadetProfile]

# Регистрация каждой модели в административной панели
for model in app_models:
    admin.site.register(model)

class RankAdmin(admin.ModelAdmin):
    search_fields = ['name']  # Замените 'name' на поле, по которому хотите выполнять поиск

admin.site.register(Rank, RankAdmin)

class CourseAdmin(admin.ModelAdmin):
    search_fields = ['name']  # Замените 'name' на поле, по которому хотите выполнять поиск

admin.site.register(Course, CourseAdmin)


class DepartamentAdmin(admin.ModelAdmin):
    list_display = ('get_department_name', 'get_platoon_name', 'display_course')
    search_fields = ['name']

    def get_department_name(self, obj):
        return obj.name
    get_department_name.short_description = 'Отделение'

    def get_platoon_name(self, obj):
        return obj.platoon.name if obj.platoon else ''
    get_platoon_name.short_description = 'Взвод'

    def display_course(self, obj):
        return obj.course.name if obj.course else ''
    display_course.short_description = 'Курс'

admin.site.register(Departament, DepartamentAdmin)

class CadetAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'display_rank', 'display_course', 'display_departament')

    autocomplete_fields = ['rank', 'course', 'departament']

    def get_full_name(self, obj):
        return f'{obj.surname} {obj.name} {obj.patronymic}'
    get_full_name.short_description = 'ФИО'

    def display_rank(self, obj):
        return obj.rank.name if obj.rank else ''
    display_rank.short_description = 'Звание'

    def display_course(self, obj):
        return obj.course.name if obj.course else ''
    display_course.short_description = 'Курс'

    def display_departament(self, obj):
        return str(obj.departament) if obj.departament else ''
    display_departament.short_description = 'Отделение'

admin.site.register(Cadet, CadetAdmin)
