from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('index/', views.index_view, name='index'),
    path('records/', views.records_view, name='records'),
    path('profile/', views.profile_view, name='profile'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('camera/', views.camera_detection_view, name='camera_detection'),
    path('avatar/', views.avatar_view, name='avatar'),
    path('image/<int:record_id>/', views.image_view, name='image'),
    path('delete_record/<int:record_id>/', views.delete_record_view, name='delete_record'),
    path('restore_record/<int:record_id>/', views.restore_record_view, name='restore_record'),
    path('permanent_delete_record/<int:record_id>/', views.permanent_delete_record_view, name='permanent_delete_record'),
    path('delete_all_records/', views.delete_all_records_view, name='delete_all_records'),
    path('restore_all_records/', views.restore_all_records_view, name='restore_all_records'),
    path('permanent_delete_all_records/', views.permanent_delete_all_records_view, name='permanent_delete_all_records'),
]