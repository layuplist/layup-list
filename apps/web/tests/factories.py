from django.contrib.auth.models import User
import factory
from apps.web import models
from lib import constants
from django.db.models.signals import post_save


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Faker("first_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        # thanks: https://gist.github.com/mbrochh/2433411
        password = factory.Faker('password')
        if 'password' in kwargs:
            password = kwargs.pop('password')
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        user.set_password(password)
        if create:
            user.save()
        return user


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

    course = factory.SubFactory(CourseFactory)

    term = constants.CURRENT_TERM
    course_registration_number = factory.Faker("random_number")
    section = factory.Faker("random_number")
    period = "2A"


class ReviewFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Review

    course = factory.SubFactory(CourseFactory)
    user = factory.SubFactory(UserFactory)

    professor = factory.Faker("name")
    term = constants.CURRENT_TERM
    comments = factory.Faker("paragraph")


class DistributiveRequirementFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.DistributiveRequirement

    name = "ART"
    distributive_type = models.DistributiveRequirement.DISTRIBUTIVE


class StudentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Student

    user = factory.SubFactory(UserFactory)
    confirmation_link = User.objects.make_random_password(length=16)


class VoteFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Vote

    value = 0
    course = factory.SubFactory(CourseFactory)
    user = factory.SubFactory(UserFactory)
    category = models.Vote.CATEGORIES.GOOD
