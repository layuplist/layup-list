from django.contrib.auth.models import User
import factory
from web import models
from lib import constants

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("first_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Course

    title = factory.Faker("words")
    department = "COSC"
    number = factory.Faker("random_number")
    url = factory.Faker("url")
    description = factory.Faker("text")

class CourseOfferingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CourseOffering

    term = constants.CURRENT_TERM
    course_registration_number = factory.Faker("random_number")
    section = factory.Faker("random_number")
    period = "2A"
    course = CourseFactory()

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Review

    course = CourseFactory()
    user = UserFactory()
    professor = factory.Faker("name")
    term = constants.CURRENT_TERM
    comments = factory.Faker("paragraph")


class DistributiveRequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DistributiveRequirement

    name = "ART"
    distributive_type = models.DistributiveRequirement.DISTRIBUTIVE
