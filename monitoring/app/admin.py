from django.contrib import admin
from .models import Faculty, Company, Platoon, Departament
from .models import Course, Rank, Cadet
from .models import Category, Exercise, ExerciseStandard, AbsenceReason, Grading


# Получение всех моделей из текущего приложения
app_models = [Faculty, Company, Platoon, Departament, Course, Rank, Cadet, Category, Exercise,
              ExerciseStandard, AbsenceReason, Grading]

# Регистрация каждой модели в административной панели
for model in app_models:
    admin.site.register(model)
