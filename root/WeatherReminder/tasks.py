
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task


def html_notification_of_city(user, city):
    title = f'Hello, {user.first_name}'
    city.update_weather()
    text = f"{city}" \
           f"<br><br>" \
           f"Weather: {city.weather}<br>" \
           f"Temperature: {city.temperature}<br>" \
           f"Humidity: {city.humidity}<br>" \
           f"<br><br>"
    return render_to_string('DWR/email.html', {'message': {'title': title, 'text': text}})


send_email_celery = shared_task(send_mail)


@shared_task(name='send_notification_to_user')
def send_notification_to_user(user, city):
    from .models import User, City
    user, city = User.objects.filter(email=user).first(), City.objects.filter(city=city).first()
    subject, message, from_email = 'Aufrutten Weather Notification System', '', None
    send_mail(subject, message, from_email, [user.email], html_message=html_notification_of_city(user, city))

