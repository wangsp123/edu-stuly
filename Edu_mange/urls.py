"""
URL configuration for Edu_mange project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from app.views import mark_attendance

urlpatterns = [
    # path('admin/', admin.site.urls),
    # 课程管理增删改
    path('course/', views.course, name='course'),
    path('delete-course/<int:id>/', views.delete_course, name='delete_course'),
    path('add-course/', views.add_course, name='add_course'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),

    # 学生信息增删改
    path('studentinfo/', views.studentinfo, name='studentinfo'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # 首页
    path('index/', views.index, name='index'),

    path('adddepart/', views.adddepart, name='adddepart'),
    path('adddepartment/', views.add_department, name='add_department'),
    path('adddexpense/', views.adddexpense, name='adddexpense'),
    path('addincome/', views.addincome, name='addincome'),
    path('addparent/', views.addparent, name='addparent'),

    path('add-employee/', views.add_employee, name='add_employee'),
    path('addstudent/', views.addstudent, name='addstudent'),

    # 部门信息增删改
    path('departinfo/', views.departinfo, name='departinfo'),
    path('delete-department/<int:id>/', views.delete_department, name='delete_department'),
    path('edit-department/<int:id>/', views.edit_department, name='edit_department'),

    path('expenses/', views.expenses, name='expenses'),
    path('financeinfo/', views.financeinfo, name='financeinfo'),
    path('income/', views.income, name='income'),
    path('parentinfo/', views.parentinfo, name='parentinfo'),
    path('recruit/', views.recruit, name='recruit'),

    # 课程表
    path('timetable/', views.timetable, name='timetable'),
    path('fullcalendar/<int:pk>/', views.fullcalendar_detail, name='fullcalendar_detail'),
    path('save_event/', views.save_event, name='save_event'),
    path('get_events/', views.get_events, name='get_events'),
    path('delete_event/', views.delete_event, name='delete_event'),
    path('get_event/<int:event_id>/', views.get_event, name='get_event'),
    path('update_event/', views.update_event, name='update_event'),
    path('get_students_by_course/', views.get_students_by_course, name='get_students_by_course'),
    path('update_student_hours/', views.update_student_hours, name='update_student_hours'),
    path('mark_attendance/<int:event_id>/', mark_attendance, name='mark_attendance'),

    # 员工信息增删改
    path('staffmange/', views.staffmange, name='staffmange'),
    path('addstaff/', views.addstaff, name='addstaff'),
    path('edit_employee/<int:id>/', views.edit_employee, name='edit_employee'),
    path('delete-employee/<int:id>/', views.delete_employee, name='delete_employee'),

    path('chievementsl/', views.chievementsl, name='chievementsl'),
    path('update/', views.update, name='update'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    #  财务信息
    path('add_income/', views.add_income, name='add_income'),
    path('add_dexpense', views.add_dexpense, name='add_dexpense'),

    # 招生信息
    path('delete_enrollment/', views.delete_enrollment, name='delete_enrollment'),
    path('update_enrollment/', views.update_enrollment, name='update_enrollment'),
    path('get_enrollment/<int:id>/', views.get_enrollment, name='get_enrollment'),
    path('update_follow_up_status/<int:id>/', views.update_follow_up_status, name='update_follow_up_status'),
    path('add_follow_up/', views.add_follow_up, name='add_follow_up'),
    path('get_enrollment_follow_up/<int:enrollment_id>/', views.get_enrollment_follow_up, name='get_enrollment_follow_up'),
    path('admin/', admin.site.urls),

    #账户相关
    path('profile/', views.profile_view, name='profile'),
path('settings/', views.settings_view, name='settings'),
path('activity-log/', views.activity_log_view, name='activity_log'),
    #点名相关在index页面
path('get_unmarked_courses/', views.get_unmarked_courses, name='get_unmarked_courses'),


]

