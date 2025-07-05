from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .models import Semester, Teacher, Subject, Message
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import RegisterForm, StudentForm, PhotoUpdateForm, StudentEditForm, AbsenceReasonForm
from .models import Student, Attendance, StudyMaterial
from .forms import AdminAttendanceForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
import json
from django.utils import timezone
from datetime import timedelta
import openai  # If using OpenAI API
import requests
from django.conf import settings

def home(request):
    return HttpResponse("🎓 <h1>Welcome to the Students Page!</h1>")

def html_view(request):
    return HttpResponse("<h1>Hello <span style='color:blue;'>Django</span> World!</h1>")

def homepage(request):
    return render(request, 'students/homepage.html')

@login_required
def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('my_profile')
    else:
        form = StudentForm()
    return render(request, 'students/form2.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return render(request, 'students/success.html', {'name': user.username})
    else:
        form = RegisterForm()
    
    return render(request, 'students/register.html', {'form': form})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Block teachers from using student login
            if hasattr(user, 'teacher'):
                return render(request, 'students/login.html', {'error': 'Please use the Teacher Login page.'})
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'students/login.html', {'error': 'Invalid Credentials'})
    return render(request, 'students/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')  # or any other page

@login_required
def dashboard(request):
    notices = request.user.notices.all().order_by('-created_at') if hasattr(request.user, 'notices') else []
    return render(request, 'students/dashboard.html', {'notices': notices})

@staff_member_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'students/student_list.html', {'students': students})

@login_required
def mark_attendance(request):
    today = timezone.now().date()
    # Check if today is Sunday (weekday() == 6 for Sunday in Python's datetime)
    if today.weekday() == 6:
        return render(request, 'students/attendance.html', {
            'already_marked': True,
            'message': "Sunday is a holiday. Attendance cannot be marked today."
        })
    already_marked = Attendance.objects.filter(student=request.user, date=today).exists()
    message = ""
    if request.method == "POST" and not already_marked:
        Attendance.objects.create(student=request.user, date=today)  # <-- FIXED: add date
        message = "Attendance marked for today!"
        already_marked = True
    elif already_marked:
        message = "You have already marked attendance today."
    return render(request, 'students/attendance.html', {
        'already_marked': already_marked,
        'message': message
    })

@login_required
def attendance_chart(request):
    # Get attendance count per day for the logged-in user
    data = (
        Attendance.objects.filter(student=request.user)
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    dates = [str(item['date']) for item in data]
    counts = [item['count'] for item in data]

    # Calculate total possible attendance days (excluding Sundays)
    from datetime import date, timedelta
    all_attendance_dates = Attendance.objects.values_list('date', flat=True).distinct()
    if all_attendance_dates:
        start_date = min(all_attendance_dates)
        end_date = max(all_attendance_dates)
        total_days = 0
        d = start_date
        while d <= end_date:
            if d.weekday() != 6:  # Exclude Sundays
                total_days += 1
            d += timedelta(days=1)
    else:
        total_days = 0

    attended_days = Attendance.objects.filter(student=request.user).count()
    percentage = (attended_days / total_days * 100) if total_days > 0 else 0
    meets_criteria = percentage >= 75

    return render(request, 'students/attendance_chart.html', {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
        'percentage': round(percentage, 2),
        'meets_criteria': meets_criteria,
        'attended_days': attended_days,
        'total_days': total_days,
    })

@login_required
def my_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    return render(request, 'students/my_profile.html', {'student': student})

@login_required
def update_photo(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('register_student')
    if request.method == 'POST':
        form = PhotoUpdateForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = PhotoUpdateForm(instance=student)
    return render(request, 'students/update_photo.html', {'form': form})

@login_required
def edit_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('register_student')
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = StudentEditForm(instance=student)
    return render(request, 'students/edit_profile.html', {'form': form})

@staff_member_required
def admin_mark_attendance(request):
    message = ""
    if request.method == "POST":
        form = AdminAttendanceForm(request.POST)
        if form.is_valid():
            # Prevent duplicate attendance for the same student and date
            student = form.cleaned_data['student']
            date = form.cleaned_data['date']
            if not Attendance.objects.filter(student=student, date=date).exists():
                Attendance.objects.create(student=student, date=date)
                message = "Attendance marked successfully!"
            else:
                message = "Attendance already marked for this student on this date."
    else:
        form = AdminAttendanceForm()
    return render(request, 'students/admin_mark_attendance.html', {'form': form, 'message': message})

@login_required
def attendance_table(request):
    # Get all attendance dates for this student
    attendance_qs = Attendance.objects.filter(student=request.user).order_by('date')
    attended_dates = set(a.date for a in attendance_qs)

    # Find the date range (from first to last attendance)
    if attended_dates:
        start_date = min(attended_dates)
        end_date = max(attended_dates)
    else:
        start_date = end_date = timezone.now().date()

    # Build a list of all days in the range (excluding Sundays)
    days = []
    d = start_date
    while d <= end_date:
        if d.weekday() != 6:  # Exclude Sundays
            days.append(d)
        d += timedelta(days=1)

    # Build attendance status for each day
    attendance_list = []
    for day in days:
        status = "P" if day in attended_dates else "A"
        attendance_list.append({
            "date": day,
            "day_name": day.strftime("%A"),
            "status": status,
        })

    return render(request, 'students/attendance_table.html', {
        "attendance_list": attendance_list,
    })

@staff_member_required
def admin_attendance_table(request):
    # Get all attendance records, newest first
    attendance_qs = Attendance.objects.select_related('student').order_by('-date')
    attendance_list = []
    for record in attendance_qs:
        # Get the Student object for extra info (name, photo)
        try:
            student_profile = Student.objects.get(user=record.student)
        except Student.DoesNotExist:
            student_profile = None
        attendance_list.append({
            "date": record.date,
            "name": student_profile.name if student_profile else record.student.username,
            "photo": student_profile.image.url if student_profile and student_profile.image else None,
            "status": "P",  # Present, since this record exists
        })

    # Optionally, show absentees (students with no record for a date)
    # For simplicity, only show presents here

    return render(request, 'students/admin_attendance_table.html', {
        "attendance_list": attendance_list,
    })

@staff_member_required
def admin_student_attendance_table(request, student_id):
    student = Student.objects.get(pk=student_id)
    attendance_qs = Attendance.objects.filter(student=student.user).order_by('date')
    attended_dates = set(a.date for a in attendance_qs)

    if attended_dates:
        start_date = min(attended_dates)
        end_date = max(attended_dates)
    else:
        start_date = end_date = timezone.now().date()

    days = []
    d = start_date
    while d <= end_date:
        if d.weekday() != 6:
            days.append(d)
        d += timedelta(days=1)

    attendance_list = []
    for day in days:
        status = "P" if day in attended_dates else "A"
        attendance_list.append({
            "date": day,
            "day_name": day.strftime("%A"),
            "status": status,
        })

    return render(request, 'students/attendance_table.html', {
        "attendance_list": attendance_list,
        "student": student,
        "admin_view": True,
    })

@staff_member_required
def admin_student_attendance_chart(request, student_id):
    student = Student.objects.get(pk=student_id)
    data = (
        Attendance.objects.filter(student=student.user)
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    dates = [str(item['date']) for item in data]
    counts = [item['count'] for item in data]

    all_attendance_dates = Attendance.objects.values_list('date', flat=True).distinct()
    if all_attendance_dates:
        start_date = min(all_attendance_dates)
        end_date = max(all_attendance_dates)
        total_days = 0
        d = start_date
        while d <= end_date:
            if d.weekday() != 6:
                total_days += 1
            d += timedelta(days=1)
    else:
        total_days = 0

    attended_days = Attendance.objects.filter(student=student.user).count()
    percentage = (attended_days / total_days * 100) if total_days > 0 else 0
    meets_criteria = percentage >= 75

    return render(request, 'students/attendance_chart.html', {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
        'percentage': round(percentage, 2),
        'meets_criteria': meets_criteria,
        'attended_days': attended_days,
        'total_days': total_days,
        'student': student,
        'admin_view': True,
    })

@login_required
def submit_absence_reason(request):
    if request.method == 'POST':
        form = AbsenceReasonForm(request.POST, request.FILES)
        if form.is_valid():
            date = form.cleaned_data['date']
            attendance, created = Attendance.objects.get_or_create(student=request.user, date=date)
            attendance.absence_reason = form.cleaned_data['absence_reason']
            attendance.medical_doc = form.cleaned_data['medical_doc']
            attendance.save()
            message = "Absence reason submitted successfully!"
            return render(request, 'students/submit_absence_reason.html', {'form': form, 'message': message})
    else:
        form = AbsenceReasonForm()
    return render(request, 'students/submit_absence_reason.html', {'form': form})

@login_required
def study_materials(request, semester_id):
    materials = StudyMaterial.objects.filter(semester_id=semester_id)
    return render(request, 'students/study_materials.html', {'materials': materials})

@login_required
def study_chatbot(request):
    response = ""
    if request.method == "POST":
        user_message = request.POST.get("message")
        # Try a different BlenderBot model
        api_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-1B-distill"
        headers = {}
        payload = {"inputs": user_message}
        try:
            r = requests.post(api_url, headers=headers, json=payload, timeout=20)
            data = r.json()
            if isinstance(data, dict) and "generated_text" in data:
                response = data["generated_text"]
            elif isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                response = data[0]["generated_text"]
            elif isinstance(data, dict) and "error" in data:
                response = "The AI model is currently busy or unavailable. Please try again later."
            else:
                response = str(data)
        except Exception:
            response = "Error connecting to AI service."
    return render(request, "students/study_chatbot.html", {"response": response})

def is_teacher(user):
    return hasattr(user, 'teacher')

@login_required(login_url='/teacher/login/')
@user_passes_test(lambda u: hasattr(u, 'teacher'), login_url='/teacher/login/')
def teacher_dashboard(request):
    messages = Message.objects.filter(teacher=request.user.teacher).order_by('-sent_at')
    materials = StudyMaterial.objects.filter(teacher=request.user.teacher)

    if request.method == "POST" and "reply_message_id" in request.POST:
        msg_id = request.POST.get("reply_message_id")
        reply_text = request.POST.get("reply_text")
        reply_file = request.FILES.get("reply_file")
        try:
            msg = Message.objects.get(id=msg_id, teacher=request.user.teacher)
            msg.reply = reply_text
            if reply_file:
                msg.reply_file = reply_file
            msg.replied_at = timezone.now()
            msg.save()
        except Message.DoesNotExist:
            pass

    return render(request, 'students/teacher_dashboard.html', {
        'materials': materials,
        'semesters': Semester.objects.all(),
        'messages': messages,
    })

def teacher_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            teacher = Teacher.objects.create(user=user)
            # Optionally assign subjects here
            return redirect('teacher_login')
    else:
        form = UserCreationForm()
    return render(request, 'students/teacher_signup.html', {'form': form})

def teacher_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'teacher'):
                login(request, user)
                return redirect('teacher_dashboard')
            else:
                form.add_error(None, "You are not registered as a teacher.")
    else:
        form = AuthenticationForm()
    return render(request, 'students/teacher_login.html', {'form': form})

@login_required
def student_message_teacher(request):
    teachers = Teacher.objects.all()
    if request.method == "POST":
        teacher_id = request.POST.get("teacher_id")
        content = request.POST.get("content")
        doubt_file = request.FILES.get("doubt_file")
        if teacher_id and (content or doubt_file):
            teacher = Teacher.objects.get(id=teacher_id)
            Message.objects.create(
                sender=request.user,
                teacher=teacher,
                content=content,
                doubt_file=doubt_file
            )
            return render(request, 'students/message_teacher.html', {
                'teachers': teachers,
                'success': True,
                'semesters': Semester.objects.all()
            })
    return render(request, 'students/message_teacher.html', {'teachers': teachers, 'semesters': Semester.objects.all()})

@login_required
def clear_student_chat(request, teacher_id):
    # Student clears chat with a specific teacher
    Message.objects.filter(sender=request.user, teacher_id=teacher_id).delete()
    return HttpResponseRedirect(reverse('dashboard'))

@login_required(login_url='/teacher/login/')
@user_passes_test(lambda u: hasattr(u, 'teacher'), login_url='/teacher/login/')
def clear_teacher_chat(request, student_id):
    # Teacher clears chat with a specific student
    Message.objects.filter(sender_id=student_id, teacher=request.user.teacher).delete()
    return HttpResponseRedirect(reverse('teacher_dashboard'))