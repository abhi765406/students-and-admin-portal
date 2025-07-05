from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField("Date of Birth", blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    university_roll_no = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    roll_no = models.CharField(max_length=20, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    # Optional fields
    optional_info = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    absence_reason = models.CharField(max_length=255, blank=True, null=True)
    medical_doc = models.FileField(upload_to='medical_docs/', blank=True, null=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.date}"

class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Semester 1"
    year = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.year})"

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Marks(models.Model):  # Make sure it's Marks, not Markss
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    mid_sem_marks = models.FloatField()
    total_marks = models.FloatField()

    def __str__(self):
        return f"{self.student.username} - {self.subject.name}"

class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(User, related_name='notices')

    def __str__(self):
        return self.title

class StudyMaterial(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='study_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)  # Use string 'Teacher'

    def __str__(self):
        return f"{self.title} ({self.semester.name})"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    # Add more fields if needed (e.g., qualification, photo)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)
    doubt_file = models.FileField(upload_to='doubt_files/', blank=True, null=True)  # Student's file
    sent_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)
    reply_file = models.FileField(upload_to='reply_files/', blank=True, null=True)  # Teacher's file
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.teacher.user.username}: {self.content[:30]}"