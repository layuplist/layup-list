from django.contrib import admin
from models import (
    Course,
    CourseMedian,
    CourseOffering,
    DistributiveRequirement,
    Instructor,
    Student,
    Review,
    Vote,
)

admin.site.register(Course)
admin.site.register(CourseOffering)
admin.site.register(DistributiveRequirement)
admin.site.register(Instructor)
admin.site.register(CourseMedian)
admin.site.register(Review)
admin.site.register(Vote)
admin.site.register(Student)
