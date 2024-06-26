from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# learning hierarchy

class Course(models.Model):
    name = models.IntegerField(default=1)

    def __str__(self):
        return str(self.name)


class Faculty(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, verbose_name='Факультет')

    def __str__(self):
        return f'{self.faculty} - {self.name}'


class Platoon(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name='Рота')

    def __str__(self):
        return f'{self.company} - {self.name}'


class Departament(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    platoon = models.ForeignKey(Platoon, on_delete=models.PROTECT, verbose_name='Взвод')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, default=1, verbose_name='Курс')

    def __str__(self):
        return f'{self.platoon} - {self.name} - {self.course}'

    class Meta:
        unique_together = ('name', 'platoon', 'course')
        verbose_name = 'Отделение'


# cadet


class Rank(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Cadet(models.Model):
    # Персональные данные
    name = models.CharField(max_length=255, verbose_name='Имя')
    surname = models.CharField(max_length=255, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=255, verbose_name='Отчество')
    # photo = models.ImageField(upload_to='learner_photos/', null=True, blank=True)
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT, verbose_name='Звание')
    # Информация о курсе обучения
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='Курс')
    departament = models.ForeignKey(Departament, on_delete=models.PROTECT, verbose_name='Отделение')
    photo = models.ImageField(upload_to='profile_pics/', default='static/img/author.jpg', null=True, blank=True, verbose_name='Фотография')

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'


# excercise

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Uniforms(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class UnitType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class ExerciseStandard(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    uniform_type = models.ForeignKey(Uniforms, on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True, null=True)
    value_satisfactory = models.FloatField(default=0)
    value_fine = models.FloatField(default=0)
    value_great = models.FloatField(default=0)
    koef_down_great = models.FloatField(default=1)
    koef_up_great = models.FloatField(default=0.01)
    reverse = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, default=0, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.exercise} - {self.course.name} - {self.uniform_type} -" \
               f" {self.value_satisfactory}:{self.value_fine}:{self.value_great} - " \
               f"{self.koef_down_great}:{self.koef_up_great}:{self.reverse}:{self.unit_type} - {self.description}"


class AbsenceReason(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"




class Grading(models.Model):
    student = models.ForeignKey(Cadet, on_delete=models.PROTECT)
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    uniform_type = models.ForeignKey(Uniforms, on_delete=models.PROTECT)
    absence_reason = models.ForeignKey(AbsenceReason, on_delete=models.SET_NULL, null=True, blank=True)
    result = models.FloatField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=False)
    rate = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.exercise} - {self.uniform_type} - " \
               f"{self.result if self.result is not None else self.absence_reason} - {self.datetime}"

# prepod

class Professor(models.Model):
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255)



# leader table

class LeaderData(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    leader_object = GenericForeignKey('content_type', 'object_id')
    position_delta = models.IntegerField(default=0)
    rate = models.IntegerField(default=0)
