from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Concert, ConcertAttending

class WebsiteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='testing-only-1849')
        self.concert = Concert.objects.create(concert_name='Autumn Live', duration=2, city='Almaty', date='2026-11-01')

    def test_home_and_private_concerts(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/concerts/').status_code, 302)

    def test_login_and_logout(self):
        self.client.post('/login/', {'username':'tester','password':'testing-only-1849'})
        self.assertContains(self.client.get('/concerts/'), 'Autumn Live')
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.client.post('/logout/')
        self.assertEqual(self.client.get('/concerts/').status_code, 302)

    def test_signup_creates_hashed_password(self):
        self.client.post('/signup/', {'username':'newfan','password':'fan-password-1984'})
        self.assertTrue(User.objects.get(username='newfan').check_password('fan-password-1984'))

    def test_attendance_update_is_unique_and_owned(self):
        self.client.force_login(self.user)
        for value in ['Attending','Not Attending']:
            self.client.post('/concert_attendee/', {'concert_id':self.concert.pk,'attendee_choice':value})
        self.assertEqual(ConcertAttending.objects.count(),1)
        self.assertEqual(ConcertAttending.objects.get().attending,'Not Attending')
        self.assertEqual(ConcertAttending.objects.get().user,self.user)

    def test_invalid_attendance_and_missing_concert(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post('/concert_attendee/', {'concert_id':self.concert.pk,'attendee_choice':'invalid'}).status_code,400)
        self.assertEqual(self.client.get('/concert-detail/99999').status_code,404)

    @patch('concert.views.requests.get')
    def test_microservice_pages(self, get):
        get.return_value = Mock(json=lambda:{'songs':[{'id':1,'title':'Demo Song','lyrics':'Demo lyrics'}]})
        self.assertContains(self.client.get('/songs/'), 'Demo lyrics')
        get.return_value = Mock(json=lambda:[{'id':1,'pic_url':'http://dummyimage.com/100x100','event_city':'Almaty'}])
        self.assertContains(self.client.get('/photos/'), 'https://dummyimage.com/100x100')

    @patch('concert.views.requests.get')
    def test_service_failure_is_reported(self,get):
        import requests
        get.side_effect = requests.ConnectionError()
        self.assertEqual(self.client.get('/songs/').status_code,503)

    def test_admin_requires_staff(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/admin/concert/concert/').status_code,302)
