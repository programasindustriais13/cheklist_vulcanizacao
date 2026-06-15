from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard / Main
    path('', views.dashboard, name='dashboard'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Machine CRUD
    path('machines/', views.machine_list, name='machine_list'),
    path('machines/new/', views.machine_create, name='machine_create'),
    path('machines/<int:pk>/edit/', views.machine_update, name='machine_update'),
    path('machines/<int:pk>/delete/', views.machine_delete, name='machine_delete'),
    
    # Checklist Execution & State Machine
    path('checklist/start/', views.checklist_start, name='checklist_start'),
    path('checklist/<int:session_id>/', views.checklist_execute, name='checklist_execute'),
    path('checklist/<int:session_id>/reopen/', views.checklist_reopen, name='checklist_reopen'),
    
    # Approval Flow decisions
    path('checklist/<int:session_id>/leader-decision/', views.leader_decision, name='leader_decision'),
    path('checklist/<int:session_id>/analyst-decision/', views.analyst_decision, name='analyst_decision'),
    
    # User approvals
    path('users/pending/', views.user_approval_list, name='user_approval_list'),
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    
    # Excel Exports
    path('checklist/<int:session_id>/export/', views.export_checklist_excel, name='export_checklist_excel'),
    path('dashboard/export/', views.export_dashboard_excel, name='export_dashboard_excel'),
]
