from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pending/', views.pending_tasks_view, name='pending_tasks'),
    path('completed/', views.completed_tasks_view, name='completed_tasks'),
    path('deleted/', views.deleted_tasks_view, name='deleted_tasks'),
    path('restore/<int:task_id>/', views.restore_task, name='restore_task'),
    path('add/', views.add_task, name='add_task'),
    path('edit/<int:task_id>/', views.edit_task, name='edit'),
    path('delete/<int:task_id>/', views.delete_task, name='delete'),
    path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('undo-task/<int:task_id>/', views.undo_task, name='undo_task'),
    path('focus/', views.focus_mode, name='focus_mode'),

]
