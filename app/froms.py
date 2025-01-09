# your_app/forms.py
from django import forms
from .models import department, Employee
from .models import Course
from .models import Student, HoursInfo, DaysInfo

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = department
        fields = ['name', 'head_name', 'describe', 'address', 'number']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '请输入部门名称'}),
            'head_name': forms.TextInput(attrs={'placeholder': '请输入部门负责人'}),
            'describe': forms.TextInput(attrs={'placeholder': '请输入部门描述'}),
            'address': forms.TextInput(attrs={'placeholder': '请输入部门地址'}),
            'number': forms.TextInput(attrs={'placeholder': '请输入部门电话'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'method', 'teacher', 'class_name', 'student_count', 'fee_type']
        widgets = {
            'method': forms.Select(choices=Course.COURSE_METHOD_CHOICES),
        }

    def clean_method(self):
        method = self.cleaned_data.get('method')
        if method == '班级':
            return 'offline'
        elif method == '1V1':
            return 'online'
        return method

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'age', 'gender', 'enrollment_type', 'address', 'course', 'fee', 'parent_contact', 'Admissionsteacher']

class HoursInfoForm(forms.ModelForm):
    class Meta:
        model = HoursInfo
        fields = ['course_hours', 'price_per_hour']

class DaysInfoForm(forms.ModelForm):
    class Meta:
        model = DaysInfo
        fields = ['start_date', 'end_date']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'age', 'gender', 'hire_date', 'department', 'position', 'status', 'contact_info']
