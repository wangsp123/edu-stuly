import logging

from django import forms
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from itertools import chain
from django.db.models import Q
from operator import attrgetter
from django.contrib.auth.forms import UserChangeForm
from .models import ActivityLog

from app import models
from app.models import Course, Employee, Income, Expense, Enrollment, FollowUp
from .froms import DepartmentForm, StudentForm, HoursInfoForm, DaysInfoForm, EmployeeForm
from django.contrib import messages
from .models import department, Student, HoursInfo, DaysInfo, FullCalendar
from .froms import CourseForm
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render


# 课程管理

def course(request):
    courses = models.Course.objects.all()
    form = CourseForm()
    return render(request, '课程管理.html', {'courses': courses})


def delete_course(request, id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=id)
        course.delete()
        return redirect('course')  # 替换为实际的重定向页面


def add_course(request):
    if request.method == 'POST':
        # 获取表单数据
        name = request.POST.get('course_name')
        method = request.POST.get('method')
        teacher = request.POST.get('teacher')
        class_name = request.POST.get('class_name')
        student_count = request.POST.get('student_count')
        fee_type = request.POST.get('fee_type')

        # 创建新的课程对象并保存到数据库
        Course.objects.create(
            name=name,
            method=method,
            teacher=teacher,
            class_name=class_name,
            student_count=student_count,
            fee_type=fee_type
        )

        # 保存成功后重定向到课程管理页面
        return redirect('course')

    return render(request, '课程管理.html')  # 如果不是 POST 请求，返回原页面


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course')  # 或其他重定向目标
    else:
        form = CourseForm(instance=course)

    return render(request, '课程管理.html', {'form': form, 'course': course})


def index(request):
    students = Student.objects.all()

    reminders = []

    # 检查每个学生的课时和天数
    for student in students:
        # 获取学员的课时信息
        try:
            hours_info = HoursInfo.objects.get(student=student)
            if hours_info.course_hours <= 10:
                reminder_message = f"{student.name}的课时已不足10小时，请考虑续费。"
                reminders.append(reminder_message)
        except HoursInfo.DoesNotExist:
            pass

        # 获取学员的天数信息
        try:
            days_info = DaysInfo.objects.get(student=student)
            if (days_info.end_date - days_info.start_date).days < 20:
                reminder_message = f"{student.name}的学习天数不足20天，请考虑续费。"
                reminders.append(reminder_message)
        except DaysInfo.DoesNotExist:
            pass
    # 获取新增和删除学员的信息
    # 获取最近的5条活动日志，按时间降序排列
    recent_log = ActivityLog.objects.filter(entity='student').order_by('-timestamp').first()
    recent_income_log = ActivityLog.objects.filter(entity='income').order_by('-timestamp').first()
    recent_expense_log = ActivityLog.objects.filter(entity='expense').order_by('-timestamp').first()
    # 获取最新的收支记录（根据时间判断哪个是最新的）
    latest_log = None
    if recent_income_log and recent_expense_log:
        if recent_income_log.timestamp > recent_expense_log.timestamp:
            latest_log = recent_income_log
        else:
            latest_log = recent_expense_log
    elif recent_income_log:
        latest_log = recent_income_log
    elif recent_expense_log:
        latest_log = recent_expense_log

    return render(request, 'index.html', {
        'recent_log': recent_log,
         'latest_log': latest_log,
        'reminders': reminders,  # 传递续费提醒
    })


@permission_required('app.view_student', raise_exception=True)
def studentinfo(request):
    print("当前请求用户：", request.user)

    students = models.Student.objects.all()
    courses = Course.objects.all()
    form = StudentForm()


    return render(request, '学生信息.html', {'students': students, 'courses': courses})


def add_student(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        hours_form = HoursInfoForm()  # 确保定义 hours_form
        days_form = DaysInfoForm()  # 确保定义 days_form
        courses = Course.objects.all()

        if student_form.is_valid():
            student = student_form.save()

            # Log the action in ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                entity='student',
                details=f"添加了{student.name}学员",
            )

            enrollment_type = request.POST.get('enrollment_type')

            if enrollment_type == 'hours':
                hours_form = HoursInfoForm(request.POST)
                if hours_form.is_valid():
                    hours_info = hours_form.save(commit=False)
                    hours_info.student = student
                    hours_info.save()


            elif enrollment_type == 'days':
                days_form = DaysInfoForm(request.POST)
                if days_form.is_valid():
                    days_info = days_form.save(commit=False)
                    days_info.student = student
                    days_info.save()

                    messages.success(request, f'{student.name} 已被添加。')

            return redirect('studentinfo')  # 提交成功后的重定向
    else:
        student_form = StudentForm()
        hours_form = HoursInfoForm()
        days_form = DaysInfoForm()
        courses = Course.objects.all()  # 获取所有课程

    return render(request, '添加学生信息.html', {
        'student_form': student_form,
        'hours_form': hours_form,
        'days_form': days_form,
        'courses': courses,  # 传递课程数据到模板
        'student_name': Student.name  # 传递学生姓名
    })


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = Course.objects.all()

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('studentinfo')  # 重定向回学生列表页面
    else:
        form = StudentForm(instance=student)

    return render(request, '学生信息.html', {
        'form': form,
        'student': student,
        'courses': courses,
    })


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        # Log the action in ActivityLog
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            entity='student',
            details=f"减少了{student.name}学员",
        )

        student.delete()
        messages.success(request, f'{student.name} 被删除')
        return redirect('studentinfo')  # 删除后重定向回学生列表页面


def adddepart(request):
    return render(request, '添加部门.html')


def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '部门信息已成功保存！')

    else:
        form = DepartmentForm()

    return render(request, '添加部门.html', {'form': form})


def edit_department(request, id):
    department_instance = get_object_or_404(department, id=id)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department_instance)
        if form.is_valid():
            form.save()
            return redirect('departinfo')  # 替换为实际的重定向 URL
    else:
        form = DepartmentForm(instance=department_instance)

    return render(request, '部门信息.html', {'form': form, 'department': department_instance})


def adddexpense(request):
    return render(request, '添加支出.html')


def addincome(request):
    return render(request, '添加收入.html')


def addparent(request):
    return render(request, '添加家长信息.html')


def addstaff(request):
    departments = department.objects.all()  # 获取所有部门
    return render(request, '新增员工信息.html', {'departments': departments})


def add_employee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        hire_date = request.POST.get('hire_date')
        department_id = request.POST.get('department')
        position = request.POST.get('position')  # 假设你有这个字段
        status = request.POST.get('status')
        contact_info = request.POST.get('contact_info')

        # 获取所选的部门对象
        department_obj = department.objects.get(id=department_id)

        # 创建并保存员工对象
        employee = Employee.objects.create(
            name=name,
            age=age,
            gender=gender,
            hire_date=hire_date,
            department=department_obj,
            position=position,
            status=status,
            contact_info=contact_info
        )

        # 保存后可以重定向到员工列表页或显示成功消息
        return redirect('staffmange')  # 替换为实际重定向的页面

    # 如果是 GET 请求，加载部门数据并渲染表单页面
    departments = department.objects.all()  # 获取所有部门
    return render(request, '新增员工信息.html', {'departments': departments})


def addstudent(request):
    courses = Course.objects.all()  # 获取所有部门
    return render(request, '添加学生信息.html', {'courses': courses})


def departinfo(request):
    departments = department.objects.all()
    return render(request, '部门信息.html', {'departments': departments})


def delete_department(request, id):
    if request.method == 'POST':
        department_instance = get_object_or_404(department, id=id)  # 使用全小写的名称
        department_instance.delete()
        return redirect('departinfo')  # 替换为你实际的重定向 URL


#财务信息
def expenses(request):
    expenses = Expense.objects.all()
    return render(request, '支出信息.html', {'expenses': expenses})


def financeinfo(request):
    try:
        # 获取查询参数中的起始日期、结束日期和搜索关键字
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search_query = request.GET.get('search', '').strip()

        # 查询所有的收入和支出记录
        incomes = Income.objects.all()
        expenses = Expense.objects.all()

        # 如果有日期范围的查询，进行日期过滤
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            incomes = incomes.filter(income_date__range=(start_date, end_date))
            expenses = expenses.filter(expense_date__range=(start_date, end_date))

        # 如果有搜索关键字，按类别、金额和备注进行搜索
        if search_query:
            # 对收入记录进行过滤

            incomes = incomes.filter(
                Q(category__icontains=search_query) |
                Q(amount__icontains=search_query) |
                Q(notes__icontains=search_query) |
                Q(type__icontains=search_query)  # 通过 type 进行过滤

            )
            # 对支出记录进行过滤
            expenses = expenses.filter(
                Q(category__icontains=search_query) |
                Q(amount__icontains=search_query) |
                Q(notes__icontains=search_query) |
                Q(type__icontains=search_query)  # 通过 type 进行过滤
            )

        # 把收入和支出记录按日期排序
        financial_records = sorted(
            chain(incomes, expenses),
            key=lambda record: record.income_date if hasattr(record, 'income_date') else record.expense_date,
            reverse=True
        )

        # 处理 AJAX 请求，返回 JSON 数据
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = []
            for record in financial_records:
                if hasattr(record, 'income_date'):  # 这是收入记录
                    data.append({
                        'type': '收入',
                        'category': record.category,
                        'amount': str(record.amount),
                        'date': record.income_date.strftime('%Y-%m-%d'),
                        'notes': record.notes
                    })
                elif hasattr(record, 'expense_date'):  # 这是支出记录
                    data.append({
                        'type': '支出',
                        'category': record.category,
                        'amount': str(record.amount),
                        'date': record.expense_date.strftime('%Y-%m-%d'),
                        'notes': record.notes
                    })
            return JsonResponse(data, safe=False)

        # 渲染页面，非 AJAX 请求时
        return render(request, '财务信息.html', {'financial_records': financial_records})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def income(request):
    incomes = Income.objects.all()
    return render(request, '收入信息.html', {'incomes': incomes})


def add_income(request):
    if request.method == 'POST':
        income_date = request.POST.get('income_date')
        source = request.POST.get('source')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')

        # 创建并保存收入记录
        Income.objects.create(
            income_date=income_date,
            source=source,
            category=category,
            amount=amount,
            payment_method=payment_method,
            notes=notes
        )
        # 记录收入的日志
        ActivityLog.objects.create(
            user=request.user,
            action='create',
            entity='income',
            details=f'收入:{source}-{amount} 元',
        )
        return redirect(reverse('income'))  # 假设你有一个显示收入列表的视图

    return render(request, '添加收入.html')


def add_dexpense(request):
    if request.method == 'POST':
        expense_date = request.POST.get('expense_date')
        reason = request.POST.get('reason')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')

        Expense.objects.create(
            expense_date=expense_date,
            reason=reason,
            category=category,
            amount=amount,
            payment_method=payment_method,
            notes=notes
        )
        # 记录支出的日志
        ActivityLog.objects.create(
            user=request.user,
            action='create',
            entity='expense',
            details=f'支出:{reason}-{amount} 元',
        )
        return redirect(reverse('expenses'))
    return render(request, '添加支出.html')


#家长信息
def parentinfo(request):
    return render(request, '家长信息.html')


#招生中心
def recruit(request):
    if request.method == 'GET':
        enrollments = Enrollment.objects.all()
        courses = Course.objects.all()
        employees = Employee.objects.all()
        return render(request, '招生中心.html',
                      {'enrollments': enrollments, 'courses': courses, 'employees': employees})

    if request.method == 'POST':
        # 处理表单数据
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        intended_course_id = request.POST.get('intended_course')
        enrollment_teacher_id = request.POST.get('enrollment_teacher')
        source_channel = request.POST.get('source_channel')

        # 创建 Enrollment 实例
        enrollment = Enrollment.objects.create(
            name=name,
            phone=phone,
            source_channel=source_channel,  # 添加渠道来源
            intended_course_id=intended_course_id,
            enrollment_teacher_id=enrollment_teacher_id,
            follow_up_status='待跟进',  # 设置初始状态
            last_follow_up_time=timezone.now(),
            next_follow_up_time=timezone.now() + timedelta(days=1)
        )

        # 返回 JSON 数据给前端，更新表格
        data = {
            'id': enrollment.id,
            'name': enrollment.name,
            'phone': enrollment.phone,
            'intended_course': enrollment.intended_course.name,
            'source_channel': enrollment.source_channel,
            'enrollment_teacher': enrollment.enrollment_teacher.name,
            'follow_up_status': enrollment.get_follow_up_status_display(),  # 获取状态显示
            'last_follow_up_time': enrollment.last_follow_up_time.strftime('%Y-%m-%d %H:%M'),
            'next_follow_up_time': enrollment.next_follow_up_time.strftime('%Y-%m-%d %H:%M'),
        }
        return JsonResponse({'success': True, 'data': data})  # 确保返回JSON数据


#删除
def delete_enrollment(request):
    if request.method == 'POST':
        # 解析 JSON 数据
        try:
            body = json.loads(request.body)  # 将请求体解析为 JSON
            ids = body.get('ids', [])  # 获取 'ids' 列表
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # 检查是否接收到 ids
        if not ids:
            return JsonResponse({'success': False, 'error': 'No IDs provided'}, status=400)

        # 打印 ids 检查内容
        print(ids)

        # 执行删除操作
        Enrollment.objects.filter(id__in=ids).delete()

        return JsonResponse({'success': True})


#编辑
def update_enrollment(request):
    if request.method == 'POST':
        enrollment_id = request.POST.get('id')
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)

        # 获取表单数据
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        source_channel = request.POST.get('source_channel')
        intended_course_id = request.POST.get('intended_course')
        enrollment_teacher_id = request.POST.get('enrollment_teacher')

        # 更新学员信息
        enrollment.name = name
        enrollment.phone = phone
        enrollment.source_channel = source_channel
        enrollment.intended_course_id = intended_course_id
        enrollment.enrollment_teacher_id = enrollment_teacher_id
        enrollment.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def get_enrollment(request, id):
    try:
        enrollment = Enrollment.objects.get(id=id)
        data = {
            'id': enrollment.id,
            'name': enrollment.name,
            'phone': enrollment.phone,
            'source_channel': enrollment.source_channel,
            'intended_course_id': enrollment.intended_course.id,
            'enrollment_teacher_id': enrollment.enrollment_teacher.id,
            # 添加其他需要返回的字段
        }
        return JsonResponse(data)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Enrollment not found'}, status=404)


def update_follow_up_status(request, id):
    if request.method == 'POST':
        try:
            enrollment = Enrollment.objects.get(id=id)
            data = json.loads(request.body)
            enrollment.follow_up_status = data.get('follow_up_status')
            enrollment.save()
            return JsonResponse({'success': True})
        except Enrollment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Enrollment not found'}, status=404)


def get_enrollment_follow_up(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    # 获取最近一次跟进记录
    follow_ups = enrollment.follow_ups.all().order_by('-created_at')

    # 获取所有跟进记录的备注信息
    follow_up_history = [
        {"time": follow_up.created_at.strftime("%Y-%m-%d %H:%M:%S"), "text": follow_up.follow_up_notes}
        for follow_up in follow_ups
    ]

    follow_up_data = {
        "name": enrollment.name,
        "phone": enrollment.phone,
        "source_channel": enrollment.source_channel,
        "follow_up_status": enrollment.follow_up_status,
        "last_follow_up_time": enrollment.last_follow_up_time,
        "next_follow_up_time": enrollment.next_follow_up_time,
        "follow_up_notes": follow_up_history[0]['text'] if follow_up_history else "",  # 获取最新的跟进备注
        "history": list(follow_up_history)  # 历史跟进记录
    }

    return JsonResponse(follow_up_data)


def add_follow_up(request):
    if request.method == "POST":
        data = json.loads(request.body)
        enrollment = get_object_or_404(Enrollment, id=data['enrollment_id'])

        # 创建新的跟进记录
        FollowUp.objects.create(
            enrollment=enrollment,
            follow_up_notes=data['follow_up_notes']
        )

        # 更新 Enrollment 的最近跟进时间和下一次跟进时间
        enrollment.last_follow_up_time = data['last_follow_up_time']
        enrollment.next_follow_up_time = data['next_follow_up_time']
        enrollment.save()

        return JsonResponse({"message": "跟进信息已保存"})


# 课程表
def timetable(request):
    courses = Course.objects.all()
    classes = Course.objects.values_list('class_name', flat=True).distinct()
    teachers = Employee.objects.all()
    return render(request, '课程表.html', {
        'courses': courses,
        'classes': classes,
        'teachers': teachers
    })


def fullcalendar_detail(request, pk):
    calendar = get_object_or_404(FullCalendar, pk=pk)

    data = {
        'course': calendar.course.name,
        'class_name': calendar.course.class_name,  # 访问 course 的 class_name 字段
        'single_schedule': calendar.single_schedule,
        'repeated_schedule': calendar.repeated_schedule,
        'teacher': calendar.teacher.name
    }
    return JsonResponse(data)


logger = logging.getLogger(__name__)


@csrf_protect
def save_event(request):
    if request.method == 'POST':

        try:
            course_id = request.POST.get('course')
            class_name = request.POST.get('class_name')
            work_type = request.POST.get('work_type')
            teacher_id = request.POST.get('teacher')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            color = request.POST.get('color', 'blue')

            course = Course.objects.get(id=course_id)
            teacher = Employee.objects.get(id=teacher_id)

            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)

            if work_type == 'single':
                FullCalendar.objects.create(
                    course=course,
                    teacher=teacher,
                    start_time=start_time,
                    end_time=end_time,
                    class_name=class_name,
                    work_type=work_type,
                    color=color  # 保存颜色信息
                )
            else:
                for i in range(4):  # 保存四次，假设每周一次
                    FullCalendar.objects.create(
                        course=course,
                        teacher=teacher,
                        start_time=start_time + timedelta(weeks=i),
                        end_time=end_time + timedelta(weeks=i),
                        class_name=class_name,
                        work_type=work_type,
                        color=color  # 保存颜色信息
                    )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error saving event: {e}")
            return JsonResponse({'status': 'fail', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'fail'}, status=400)


def get_events(request):
    events = FullCalendar.objects.all()
    events_list = []
    for event in events:
        events_list.append({
            'id': event.id,
            'title': f"{event.course.name} - {event.teacher.name}",
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'color': event.color,  # 返回颜色信息
            'extendedProps': {
                'className': event.class_name,
                'workType': event.work_type,
                'courseId': event.course.id,
                'teacherId': event.teacher.id,
            }
        })
    return JsonResponse(events_list, safe=False)


@csrf_exempt
def delete_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('id')
        try:
            event = FullCalendar.objects.get(id=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except FullCalendar.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


logger = logging.getLogger(__name__)


@csrf_exempt
def update_event(request):
    if request.method == 'POST':
        try:
            event_id = request.POST.get('id')
            course_name = request.POST.get('course')
            class_name = request.POST.get('class_name')
            work_type = request.POST.get('work_type')
            teacher_name = request.POST.get('teacher')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            logger.debug(f"Received update request for event {event_id} with data: "
                         f"course={course_name}, class_name={class_name}, work_type={work_type}, "
                         f"teacher={teacher_name}, start_time={start_time}, end_time={end_time}")

            event = FullCalendar.objects.get(id=event_id)

            # 处理通过名称更新的情况
            if course_name and teacher_name:
                course = Course.objects.get(name=course_name)
                teacher = Employee.objects.get(name=teacher_name)
            # 处理通过 ID 更新的情况
            else:
                course_id = request.POST.get('course_id')
                teacher_id = request.POST.get('teacher_id')
                course = Course.objects.get(id=course_id)
                teacher = Employee.objects.get(id=teacher_id)

            event.course = course
            event.class_name = class_name
            event.work_type = work_type
            event.teacher = teacher
            event.start_time = datetime.fromisoformat(start_time)
            event.end_time = datetime.fromisoformat(end_time)
            event.save()

            logger.debug(f"Event {event_id} updated successfully")
            return JsonResponse({'status': 'success'})
        except FullCalendar.DoesNotExist:
            logger.error(f"Event {event_id} not found")
            return JsonResponse({'status': 'fail', 'error': 'Event not found'}, status=404)
        except Course.DoesNotExist:
            logger.error(f"Course not found")
            return JsonResponse({'status': 'fail', 'error': 'Course not found'}, status=404)
        except Employee.DoesNotExist:
            logger.error(f"Teacher not found")
            return JsonResponse({'status': 'fail', 'error': 'Teacher not found'}, status=404)
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return JsonResponse({'status': 'fail', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'fail'}, status=400)


def get_event(request, event_id):
    event = get_object_or_404(FullCalendar, id=event_id)
    event_data = {
        "id": event.id,
        "title": f"{event.course.name} - {event.teacher.name}",
        "start": event.start_time.isoformat(),
        "end": event.end_time.isoformat(),
        'color': event.color,  # 返回颜色信息
        "extendedProps": {
            "className": event.class_name,
            "workType": event.work_type,

        }
    }
    return JsonResponse(event_data)


# 课程表点名视图获取课时的学生
def get_students_by_course(request):
    course_name = request.GET.get('course_name')
    students = Student.objects.filter(course__name=course_name)
    student_list = [{'id': student.id, 'name': student.name} for student in students]
    return JsonResponse({'students': student_list})


@csrf_exempt
def update_student_hours(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('attendance_data'))
        for item in data:
            student_id = item['student_id']
            consumed_hours = int(item['consumed_hours'])
            try:
                student = Student.objects.get(id=student_id)
                hours_info = HoursInfo.objects.get(student=student)
                hours_info.course_hours -= consumed_hours
                hours_info.save()
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)
            except HoursInfo.DoesNotExist:
                return JsonResponse({'error': 'HoursInfo not found'}, status=404)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def mark_attendance(request, event_id):
    if request.method == 'POST':
        try:
            event = FullCalendar.objects.get(id=event_id)
            event.color = '#FFC0CB'  # 粉色
            event.save()
            return JsonResponse({'status': 'success', 'message': '点名成功，颜色已更新'})
        except FullCalendar.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '事件不存在'})
    return JsonResponse({'status': 'error', 'message': '无效请求'})


#
#
#


#员工管理
def staffmange(request):
    employees = Employee.objects.all()  # 获取所有员工
    departments = department.objects.all()  # 获取所有部门

    return render(request, '员工信息表.html', {
        'employees': employees,
        'departments': departments  # 传递所有部门信息到模板
    })


def edit_employee(request, id):
    # 获取要编辑的员工对象
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        # 从表单中获取更新后的员工信息
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('staffmange')  # 编辑完成后，重定向到员工管理页面
    else:
        # 如果是GET请求，渲染编辑页面，传递员工信息
        form = EmployeeForm(instance=employee)

    # 获取所有部门
    departments = department.objects.all()
    return render(request, '员工信息表.html', {
        'form': form,
        'employee': employee,
        'departments': departments
    })


def delete_employee(request, id):
    # 获取要删除的员工对象
    employee = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        # 删除员工对象
        employee.delete()

        # 删除后，重定向到员工管理页面
        return redirect('staffmange')

    return redirect('staffmange')  # 若直接访问此URL，也重定向回员工管理页面


def chievementsl(request):
    return render(request, '学生成绩单.html')


def update(request):
    return render(request, '修改学生信息.html')





def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 验证用户名和密码
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # 用户认证通过后登录
            return redirect('index')  # 重定向到主页，假设 'index' 是你在 urls.py 中定义的名称
        else:
            messages.error(request, '注意：用户名或密码错误')
            return redirect('login')  # 登录失败，重定向回登录页面
    print(f"当前请求用户：{request.user}")

    return render(request, '登录.html')

def logout_view(request):
    logout(request)  # 清除当前会话中的用户信息
    return redirect('login')  # 登出后跳转到登录页面

def register(request):
    return render(request, '注册.html')


@login_required
def profile_view(request):
    user = request.user  # 获取当前登录用户
    return render(request, 'profile.html', {'user': user})


@login_required
def settings_view(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # 更新后重定向到个人资料页面
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'settings.html', {'form': form})

@login_required
def activity_log_view(request):
    user = request.user
    logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')  # 根据时间排序日志
    return render(request, 'activity_log.html', {'logs': logs})


def get_unmarked_courses(request):
    now = timezone.now()
    one_hour_ago = now - timezone.timedelta(hours=1)
    unmarked_courses = FullCalendar.objects.filter(start_time__lte=one_hour_ago, color='blue')  # 假设'blue'表示未点名
    data = [
        {
            'id': course.id,
            'name': course.class_name,
            'teacher_name': course.teacher.name,  # 假设Employee模型有一个name字段
            'start_time': course.start_time
        }
        for course in unmarked_courses
    ]
    return JsonResponse({'unmarked_courses': data})
