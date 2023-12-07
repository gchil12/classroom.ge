from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse
from app_teacher.views import (
    teacher_homepage,
    classroom_details,
    archive_classroom,
    delete_classroom,
    new_classroom,
    new_lesson,
    delete_lesson,
)
from uuid import uuid4


class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('app_teacher:home')
        self.assertEquals(resolve(url).func, teacher_homepage)


    def test_classrooom_url_is_resolved(self):
        url = reverse('app_teacher:classroom-detail', kwargs={'uuid': uuid4()})
        self.assertEquals(resolve(url).func, classroom_details)


    def test_archive_classroom_url_is_resolved(self):
        url = reverse('app_teacher:classroom-archive', kwargs={'uuid': uuid4()})
        self.assertEquals(resolve(url).func, archive_classroom)


    def test_delete_classroom_url_is_resolved(self):
        url = reverse('app_teacher:classroom-delete', kwargs={'uuid': uuid4()})
        self.assertEquals(resolve(url).func, delete_classroom)


    def test_new_classroom_url_is_resolved(self):
        url = reverse('app_teacher:create-new-classroom')
        self.assertEquals(resolve(url).func, new_classroom)


    def test_new_lesson_url_is_resolved(self):
        url = reverse('app_teacher:create-new-lesson', kwargs={'classroom_uuid': uuid4()})
        self.assertEquals(resolve(url).func, new_lesson)


    def test_delete_lesson_url_is_resolved(self):
        url = reverse('app_teacher:lesson-delete', kwargs={'uuid': uuid4()})
        self.assertEquals(resolve(url).func, delete_lesson)

