from django.urls import path
from .views import index, login_view, control, author, test_page, add_results, edit_users, \
    get_exercises_for_category, get_exercise_standard, get_cadets_from_dep, save_grading_data, edit_groups, \
    update_group, delete_group, delete_user, update_user, editing_page, get_editing_table, save_new_obj, delete_object,\
    update_object, get_leaderboards, get_user_data
from .views import edit_platoons, update_platoon, delete_platoon, edit_companies, update_company, delete_company,\
    edit_faculty, update_faculty, delete_faculty, report
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='app:login'), name='logout'),
    path('control/', control, name='control'),

    path('author/', author, name='author'),
    path('test_page/', test_page, name='test_page'),
    path('edit_users/', edit_users, name='edit_users'),
    path('update_user/<int:pk>/', update_user, name='update_user'),
    path('delete_user/<int:pk>/', delete_user, name='delete_user'),
    path('edit_groups/', edit_groups, name='edit_groups'),
    path('update_group/<int:pk>/', update_group, name='update_group'),
    path('delete_group/<int:pk>/', delete_group, name='delete_group'),

    path('edit_platoons/', edit_platoons, name='edit_platoons'),
    path('update_platoon/<int:pk>/', update_platoon, name='update_platoon'),
    path('delete_platoon/<int:pk>/', delete_platoon, name='delete_platoon'),

    path('edit_companies/', edit_companies, name='edit_companies'),
    path('update_company/<int:pk>/', update_company, name='update_company'),
    path('delete_company/<int:pk>/', delete_company, name='delete_company'),

    path('edit_faculty/', edit_faculty, name='edit_faculty'),
    path('update_faculty/<int:pk>/', update_faculty, name='update_faculty'),
    path('delete_faculty/<int:pk>/', delete_faculty, name='delete_faculty'),

    path('editing_page/', editing_page, name='editing_page'),
    path('get_editing_table/', get_editing_table, name='get_editing_table'),
    path('save_new_obj/', save_new_obj, name='save_new_obj'),
    path('delete_object/<str:obj>/<int:pk>/', delete_object, name='delete_object'),
    path('update_object/<str:obj>/<int:pk>/', update_object, name='update_object'),

    path('add_results/', add_results, name='add_results'),
    path('get_exercises_for_category/<int:category_id>/',
         get_exercises_for_category, name='get_exercises_for_category'),
    path('get_exercise_standard/<int:exercise_id>/<int:departament_id>/<int:uniform_id>/',
         get_exercise_standard, name='get_exercise_standard'),
    path("get_cadets_from_dep/<int:departament_id>/",
         get_cadets_from_dep, name='get_cadets_from_dep'),
    path('save_grading_data/', save_grading_data, name='save_grading_data'),

    path('get_leaderboards/', get_leaderboards, name='get_leaderboards'),
    path('get_user_data/<int:pk>/', get_user_data, name='get_user_data'),

    path('report/', report, name='report'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
