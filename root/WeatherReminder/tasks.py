
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task

from .models import User, City


send_email_celery = shared_task(send_mail, name='celery_async_send_email')


def html_notification_of_city(user, city):
    """rendering the html with city's for user"""
    city.update_weather()
    title = f'Hello, {user.first_name}'
    text = f"{city}" \
           f"<br><br>" \
           f"Weather: {city.weather}<br>" \
           f"Temperature: {city.temperature}<br>" \
           f"Humidity: {city.humidity}<br>" \
           f"<br><br>"
    return render_to_string('DWR/email.html', {'message': {'title': title, 'text': text}})


@shared_task(name='send_notification_to_user')
def send_notification_to_user(user, city):
    user, city = User.objects.filter(email=user).first(), City.objects.filter(city=city).first()
    subject, message, from_email = 'Aufrutten Weather Notification System', '', None
    send_mail(subject, message, from_email, [user.email], html_message=html_notification_of_city(user, city))

