import asyncio
import time
import threading
import bisect

import django
from django.utils import timezone
from asgiref.sync import sync_to_async, async_to_sync


class Reminder:

    def __init__(self):
        from . import models
        users = models.User.objects.filter(is_active=True, notification_is_enable=True, subscriptions=True)
        self.list_of_users = list(users.all().order_by('next_notifications'))
        self.status_loop = False
        self.__start_loop()

    def __call__(self, *args, **kwargs):
        self.__start_loop()

    def __start_loop(self):
        if not self.status_loop:
            thread = threading.Thread(target=self.__loop)
            thread.daemon = True
            thread.start()

    def update_into_queue(self, user):
        if user in self.list_of_users:
            self.remove_from_queue(user)
            self.add_to_queue(user)
            self.__start_loop()

    def add_to_queue(self, user):
        q_list = self.list_of_users
        if user.is_active and user.notification_is_enable and user.subscriptions.first() and user not in q_list:
            bisect.insort(self.list_of_users, user)
            self.__start_loop()

    def remove_from_queue(self, user):
        if user in self.list_of_users:
            self.list_of_users.remove(user)

    def __loop(self):
        self.status_loop = True
        while self.list_of_users:
            user = self.list_of_users[0]
            if timezone.now() >= user.next_notifications:
                async_to_sync(user.send_notifications)()
                self.update_into_queue(user)

            else:
                diff_time = user.next_notifications - timezone.now()
                time.sleep(diff_time.seconds)

        self.status_loop = False


try:
    reminder = Reminder()

except django.db.utils.OperationalError:
    pass
