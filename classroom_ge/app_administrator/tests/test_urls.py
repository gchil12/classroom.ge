from django.test import SimpleTestCase
from django.urls import resolve, reverse
from app_administrator.views import home

class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('app_administrator:home')
        self.assertEquals(resolve(url).func, home)
