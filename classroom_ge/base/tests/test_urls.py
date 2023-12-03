from django.test import SimpleTestCase
from django.urls import resolve, reverse
from base.views import home, register, loginUser, logoutUser

class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('app_base:home')
        self.assertEquals(resolve(url).func, home)


    def test_register_url_is_resolved(self):
        url = reverse('app_base:register')
        self.assertEquals(resolve(url).func, register)


    def test_login_url_is_resolved(self):
        url = reverse('app_base:login')
        self.assertEquals(resolve(url).func, loginUser)


    def test_logout_url_is_resolved(self):
        url = reverse('app_base:logout')
        self.assertEquals(resolve(url).func, logoutUser)