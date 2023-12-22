from django.db import models
from django.utils import timezone

# learning hierarchy

class Faculty(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.faculty} - {self.name}'


class Platoon(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.company} - {self.name}'


class Departament(models.Model):
    name = models.CharField(max_length=255)
    platoon = models.ForeignKey(Platoon, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.platoon} - {self.name}'


# cadet

class Course(models.Model):
    name = models.IntegerField()

    def __str__(self):
        return str(self.name)


class Rank(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Cadet(models.Model):
    # Персональные данные
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    # photo = models.ImageField(upload_to='learner_photos/', null=True, blank=True)
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT)

    # Информация о курсе обучения
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    departament = models.ForeignKey(Departament, on_delete=models.PROTECT)

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


class ExerciseStandard(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    description = models.CharField(max_length=255)
    value = models.FloatField()

    def __str__(self):
        return f"{self.exercise} - {self.course.name} - {self.value} - {self.description}"


class AbsenceReason(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Grading(models.Model):
    student = models.ForeignKey(Cadet, on_delete=models.PROTECT)
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    absence_reason = models.ForeignKey(AbsenceReason, on_delete=models.SET_NULL, null=True, blank=True)
    result = models.FloatField(blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name} - {self.exercise.name} - " \
               f"{self.result if self.result is not None else self.absence_reason.name} - {self.datetime}"

# prepod

class Professor(models.Model):
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
