import django
from django.contrib.auth.models import User
from django.db import models,migrations
from django import forms
from django.utils import timezone



class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', '创建'),
        ('delete', '删除'),
        ('update', '更新'),
        ('retrieve', '查询'),
    ]

    ENTITY_CHOICES = [
        ('student', '学员'),
        ('income', '收入'),
        # 添加其他实体类型
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    entity = models.CharField(max_length=50, choices=ENTITY_CHOICES,default='student')
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"

    class Meta:
        verbose_name = "活动日志"
        verbose_name_plural = "活动日志"
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
        ]
# Create your models here.
# 创建课程管理表
class Course(models.Model):
    COURSE_METHOD_CHOICES = [
        ('online', '1V1'),
        ('offline', '班级'),
    ]

    name = models.CharField(max_length=100, verbose_name="课程名称")
    method = models.CharField(max_length=10, choices=COURSE_METHOD_CHOICES, verbose_name="授课方式")
    teacher = models.CharField(max_length=100, verbose_name="教师")
    class_name = models.CharField(max_length=100, verbose_name="班级")
    student_count = models.IntegerField(verbose_name="学员人数")
    fee_type = models.CharField(max_length=50, verbose_name="收费类型/课时")

    def __str__(self):
        return self.name


# 创建学生信息表格
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]

    ENROLLMENT_TYPE_CHOICES = [
        ('hours', '课时'),
        ('days', '天数'),
    ]

    name = models.CharField(max_length=100, verbose_name="姓名")
    age = models.IntegerField(verbose_name="年龄",blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="性别",blank=True)
    enrollment_type = models.CharField(max_length=10, choices=ENROLLMENT_TYPE_CHOICES, verbose_name="报课方式")
    address = models.CharField(max_length=255, verbose_name="家庭住址",blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name="课程")
    fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="学费")
    parent_contact = models.CharField(max_length=100, verbose_name="家长联系方式",blank=True)
    Admissionsteacher = models.CharField(max_length=100, verbose_name="招生老师",blank=True)


    def __str__(self):
        return self.name


class HoursInfo(models.Model):
    student = models.OneToOneField('Student', on_delete=models.CASCADE, primary_key=True)
    course_hours = models.IntegerField(verbose_name="课时长")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")

    def __str__(self):
        return f"{self.course_hours}小时 @ {self.price_per_hour}元/小时"


class DaysInfo(models.Model):
    student = models.OneToOneField('Student', on_delete=models.CASCADE, primary_key=True)
    start_date = models.DateField(verbose_name="开始时间")
    end_date = models.DateField(verbose_name="结束时间")

    def __str__(self):
        return f"{self.start_date} 到 {self.end_date}"

#创建部门信息表格
class department(models.Model):
    name = models.CharField(max_length=100, verbose_name="部门名称")
    head_name = models.CharField(max_length=10,  verbose_name="部门负责人")
    describe = models.CharField(max_length=100, verbose_name="部门描述" ,blank=True)
    address = models.CharField(max_length=100, verbose_name="部门地址",blank=True)
    number = models.CharField( max_length=11,  verbose_name="部门电话" ,blank=True)

    def __str__(self):
       return self.name



# 员工信息表格
class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]

    STATUS_CHOICES = [
        ('active', '在职'),
        ('inactive', '离职'),
    ]


    name = models.CharField(max_length=100, verbose_name="姓名")
    age = models.IntegerField(verbose_name="年龄")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="性别")
    hire_date = models.DateField(verbose_name="入职时间")
    department = models.ForeignKey(department, on_delete=models.CASCADE, verbose_name="所属部门")
    position = models.CharField(max_length=100, verbose_name="职位")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="当前状态", default='active')
    contact_info = models.CharField(max_length=100, verbose_name="联系方式" , blank=True, default='Unknown')

    def __str__(self):
        return f"{self.name} "



#课程表
class FullCalendar(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # 课程外键
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE)  # 教师外键
    start_time = models.DateTimeField()  # 开始时间
    end_time = models.DateTimeField()  # 结束时间
    class_name = models.CharField(max_length=100)  # 班级名称
    work_type = models.CharField(max_length=20, choices=[('single', '自由排课'), ('repeated', '重复排课')], default='single')# 排课方式
    color = models.CharField(max_length=20, default='blue')  # 颜色字段，默认值为蓝色


#收入表
class Income(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('WX', '微信'),
        ('ZFB', '支付宝'),
        ('CC', '信用卡'),
        ('BC', '银行卡'),
        ('OTHER', '其他'),
    ]

    income_date = models.DateField(verbose_name='收入日期')
    source = models.CharField(max_length=255, verbose_name='收入来源')
    category = models.CharField(max_length=255, verbose_name='收入类别')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    payment_method = models.CharField(max_length=5, choices=PAYMENT_METHOD_CHOICES, verbose_name='支付方式')
    notes = models.TextField(blank=True, null=True, verbose_name='备注信息')
    type = models.CharField(max_length=10, default='收入', verbose_name='类别')

    @property
    def date(self):
        return self.income_date  # 返回收入日期


    def __str__(self):
        return f"{self.source} - {self.amount} ({self.income_date})"

#支出表
class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('WX', '微信'),
        ('ZFB', '支付宝'),
        ('CC', '信用卡'),
        ('BC', '银行卡'),
        ('GTT', '对公转账'),
        ('OTHER', '其他'),
    ]

    expense_date = models.DateField(verbose_name='支出日期')
    reason = models.CharField(max_length=255, verbose_name='支出原因')
    category = models.CharField(max_length=255, verbose_name='支出类别')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    payment_method = models.CharField(max_length=5, choices=PAYMENT_METHOD_CHOICES, verbose_name='支付方式')
    notes = models.TextField(blank=True, null=True, verbose_name='备注信息')
    type = models.CharField(max_length=10, default='支出', verbose_name='类别')

    @property
    def date(self):
        return self.expense_date  # 返回支出日期



    def __str__(self):
        return f"{self.reason} - {self.amount} ({self.expense_date})"



#招生信息表
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('失效', '失效'),
        ('跟进中', '跟进中'),
        ('待跟进', '待跟进'),
        ('已签约', '已签约'),
        ('已邀约', '已邀约'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    source_channel = models.CharField(max_length=100, blank=True)
    follow_up_status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    last_follow_up_time = models.DateTimeField()
    next_follow_up_time = models.DateTimeField()
    intended_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_teacher = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class FollowUp(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_notes = models.CharField(max_length=120)
    created_at = models.DateTimeField( default=timezone.now)  # 自动记录创建时间

    def __str__(self):
        return f"{self.enrollment.name} - {self.created_at}"
