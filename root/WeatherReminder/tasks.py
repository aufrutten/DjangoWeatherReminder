
from django_celery_beat.models import PeriodicTask
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task

from .models import User, City, Subscription


# celery async function overload the default function 'django.core.mail.send_email'
send_email_celery = shared_task(send_mail, name='celery_async_send_email')


def get_html_content_about_city(city):
    """getting small part of city in html view"""
    city.update_weather()  # update weather with JSON config rules
    html = f"{city}" \
           f"<br><br>" \
           f"Weather: {city.weather}<br>" \
           f"Temperature: {city.temperature}<br>" \
           f"Humidity: {city.humidity}<br>" \
           f"<br><br>"
    return html


def render_html_notifications(user, subscriptions):
    """rendering the html with city's for user"""
    title = f'Hello, {user.first_name}'
    html = []
    for subscription in subscriptions:
        city = get_html_content_about_city(subscription.city)
        html.append(city)
    html_response = '<br><br>'.join(html)
    return render_to_string('DWR/email.html', {'message': {'title': title, 'text': html_response}})


@shared_task(name='send_notification_to_user')
def send_notification_to_user(user, frequency):
    """celery task with name 'send_notification_to_user' rendering and sending html email"""
    user = User.objects.filter(email=user).first()
    subscriptions = Subscription.objects.filter(user=user, frequency_update=frequency).all()
    subject, message, from_email = 'Aufrutten Weather Notification System', '', None
    if subscriptions:  # if we have one or more subscription, do rendering and sending
        html_message = render_html_notifications(user, subscriptions)
        send_mail(subject, message, from_email, [user.email], html_message=html_message)
    else:  # else, delete the task to unload system
        task = PeriodicTask.objects.filter(name=f'{user}:{frequency}H').first()
        task.delete()

