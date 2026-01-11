from django.urls import path
from .import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path("stats/", views.dashboard_stats, name="dashboard_stats"),

  
    path("mark/<str:staff_id>/", views.mark_attendance, name="mark_attendance"),


   path("reports/", views.dashboard_reports, name="dashboard_reports"),
   path("reports/pdf/", views.download_report_pdf, name="download_report_pdf"),
   path("reports/excel/", views.download_report_excel, name="download_report_excel"),
   path('reports/download/pdf/', views.download_report_pdf, name='download_report_pdf'),


    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Staff management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:pk>/delete/', views.delete_staff, name='delete_staff'),
]


