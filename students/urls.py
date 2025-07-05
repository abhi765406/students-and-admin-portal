from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # when you visit /students/
    path('hello/', views.html_view),
    path('homepage/', views.homepage),  # visit /students/homepage/
    path('register/', views.register_student, name='register_student'),
    path('signup/', views.register_user, name='signup'),
    path('login/', views.login_user, name='login'),      # <-- add name
    path('logout/', views.logout_user, name='logout'),   # <-- add name
    path('list/', views.student_list, name='student_list'),
    # path('students/templates/students/student_list.html', views.student_list, name='student_list_template'),
    path('attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance/chart/', views.attendance_chart, name='attendance_chart'),
    path('attendance/table/', views.attendance_table, name='attendance_table'),
    path('profile/', views.my_profile, name='my_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-photo/', views.update_photo, name='update_photo'),
]

urlpatterns += [
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]

urlpatterns += [
    path('admin/mark-attendance/', views.admin_mark_attendance, name='admin_mark_attendance'),
]

urlpatterns += [
    path('admin/attendance-table/', views.admin_attendance_table, name='admin_attendance_table'),
]

urlpatterns += [
    path('admin/student/<int:student_id>/attendance-table/', views.admin_student_attendance_table, name='admin_student_attendance_table'),
    path('admin/student/<int:student_id>/attendance-chart/', views.admin_student_attendance_chart, name='admin_student_attendance_chart'),
]

urlpatterns += [
    path('absence-reason/', views.submit_absence_reason, name='submit_absence_reason'),
]

urlpatterns += [
    path('materials/<int:semester_id>/', views.study_materials, name='study_materials'),
]

urlpatterns += [
    path('study-chatbot/', views.study_chatbot, name='study_chatbot'),
]

urlpatterns += [
    path('teacher/signup/', views.teacher_signup, name='teacher_signup'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
]

urlpatterns += [
    path('message-teacher/', views.student_message_teacher, name='message_teacher'),
]

urlpatterns += [
    path('clear_chat/<int:teacher_id>/', views.clear_student_chat, name='clear_student_chat'),
    path('teacher/clear_chat/<int:student_id>/', views.clear_teacher_chat, name='clear_teacher_chat'),
]