from django.urls import path
from . import views

urlpatterns = [
    # Reports
    path('reports/',                    views.ReportListCreateView.as_view()),
    path('reports/<int:pk>/',           views.ReportDetailView.as_view()),
    path('reports/<int:pk>/assign/',    views.AssignCounselorView.as_view()),
    path('reports/<int:pk>/appointment/',         views.AppointmentView.as_view()),
    path('reports/<int:pk>/appointment/respond/', views.AppointmentRespondView.as_view()),
    path('reports/<int:pk>/session-report/',      views.SessionReportView.as_view()),
    path('reports/<int:pk>/schedule/',            views.StudentScheduleView.as_view()),

    # Counselors
    path('counselors/',                 views.CounselorListCreateView.as_view()),
    path('counselors/<int:pk>/',        views.CounselorDetailView.as_view()),
    path('counselors/me/',              views.CounselorProfileView.as_view()),

    # Students (director only)
    path('students/',                    views.StudentListView.as_view()),
    path('students/import/',             views.StudentImportView.as_view()),
    path('students/<int:pk>/activate/',  views.ActivateStudentView.as_view()),
    path('students/<int:pk>/reset-password/', views.StudentResetPasswordView.as_view()),
    path('students/<int:pk>/',           views.StudentDetailView.as_view()),

    # Dashboard stats
    path('stats/',                      views.StatsView.as_view()),

    # Annonces
    path('annonces/',                   views.AnnonceListCreateView.as_view()),
    path('annonces/<int:pk>/',          views.AnnonceDetailView.as_view()),

    # Activités
    path('activites/',                  views.ActiviteListCreateView.as_view()),
    path('activites/<int:pk>/',         views.ActiviteDetailView.as_view()),

    # Contenu du site
    path('site-content/',               views.SiteContentView.as_view()),

    # Photos
    path('photos/',                     views.PhotoListCreateView.as_view()),
    path('photos/<int:pk>/',            views.PhotoDetailView.as_view()),

    # Notifications
    path('notifications/',               views.NotificationListView.as_view()),
    path('notifications/read-all/',      views.NotificationReadAllView.as_view()),
    path('notifications/<int:pk>/read/', views.NotificationDetailView.as_view()),

    # Change password (premier login forcé)
    path('auth/change-password/',        views.ChangePasswordView.as_view()),
]
