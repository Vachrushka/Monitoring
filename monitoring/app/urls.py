from django.urls import path, include
from .views import index, login_view, control, author, test_page, add_results, editing, get_exercises_for_category
from django.contrib.auth import views as auth_views

app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='app:login'), name='logout'),
    path('control/', control, name='control'),
    path('author/', author, name='author'),
    path('test_page/', test_page, name='test_page'),
    path('editing/', editing, name='editing'),
    path('add_results/', add_results, name='add_results'),
    path('get_exercises_for_category/<int:category_id>/', get_exercises_for_category, name='get_exercises_for_category'),

]
