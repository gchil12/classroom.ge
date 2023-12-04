from django.test import TestCase, Client
from django.urls import reverse
import json
from base.models import User

class TestViews(TestCase):
    def setUp(self) -> None:
        self.email = 'testemail@gmail.com'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            password=self.password,
            name='name',
            surname='surname',
            date_of_birth='1995-05-23',
            is_student=True,
            email=self.email,
            school='school',
            city='city',
        )
        
        self.client = Client()
        self.home_url = reverse('app_base:home')
        self.register_url = reverse('app_base:register')
        self.login_url = reverse('app_base:login')
        self.logout_url = reverse('app_base:logout')


    def test_homep_GET(self):
        response = self.client.get(self.home_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')


    def test_register_GET(self):
        response = self.client.get(self.register_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/register.html')


    def test_login_GET(self):
        response = self.client.get(self.login_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login.html')


    def test_logout_POST(self):
        self.client.login(email=self.email, password=self.password)

        response = self.client.get(self.logout_url)
        
        self.assertEquals(response.status_code, 302)

        redirected_response = self.client.get(response.url)

        self.assertEquals(redirected_response.status_code, 200)
        self.assertTemplateUsed(redirected_response, 'base/home.html')