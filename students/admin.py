from django.contrib import admin
from .models import Student, Attendance, Semester, Subject, Marks, Notice, StudyMaterial, Teacher
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import User, Group

class CustomAdminSite(admin.AdminSite):
    site_header = "College Portal Admin"
    site_title = "College Portal Admin"
    index_title = "Welcome to College Portal Admin"

    def each_context(self, request):
        context = super().each_context(request)
        context['custom_admin_css'] = True
        return context

admin.site = CustomAdminSite()

class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'photo_tag', 'semester_list', 'internal_marks_list',
        'attendance_table_link', 'attendance_chart_link'
    )

    def photo_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:50%;" />', obj.image.url)
        return "No Image"
    photo_tag.short_description = 'Photo'

    def semester_list(self, obj):
        semesters = Semester.objects.filter(
            subject__marks__student=obj.user
        ).distinct()
        return ", ".join([s.name for s in semesters]) if semesters else "N/A"
    semester_list.short_description = 'Semesters'

    def internal_marks_list(self, obj):
        marks = Marks.objects.filter(student=obj.user)
        if not marks:
            return "N/A"
        # Show subject code and marks, e.g. "MATH101: 18, PHY102: 20"
        return format_html("<br>".join(
            f"{m.subject.code}: {m.mid_sem_marks}/{m.total_marks}" for m in marks
        ))
    internal_marks_list.short_description = 'Internal Marks'

    def attendance_table_link(self, obj):
        url = reverse('admin_student_attendance_table', args=[obj.pk])
        return format_html('<a class="button" href="{}">Attendance Table</a>', url)
    attendance_table_link.short_description = 'Attendance Table'

    def attendance_chart_link(self, obj):
        url = reverse('admin_student_attendance_chart', args=[obj.pk])
        return format_html('<a class="button" href="{}">Attendance Chart</a>', url)
    attendance_chart_link.short_description = 'Attendance Chart'

admin.site.register(Student, StudentAdmin)
admin.site.register(Attendance)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(Marks)
admin.site.register(Notice)
admin.site.register(StudyMaterial)
admin.site.register(User)
admin.site.register(Group)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('subjects',)

admin.site.register(Teacher, TeacherAdmin)