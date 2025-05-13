#task_manager\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  #pagina de home
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('create-task/', views.create_task, name='create_task'),
    path('delete-task/',views.delete_tasks, name='delete_tasks'),
    path('task/<int:task_id>/', views.edit_task, name='edit-task'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('api/delete-notificare/<int:id_notif>/', views.delete_notificare_api, name='delete_notificare_api'),
    path('update-task-completion/', views.update_task_completion, name='update_task_completion'),
    path('sort-ai/', views.ai_prioritize_user_tasks, name='ai_prioritize_user_tasks'),
]