from django.test import SimpleTestCase
from django.urls import resolve, reverse
from app_student.views import student_homepage

class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('app_student:home')
        self.assertEquals(resolve(url).func, student_homepage)