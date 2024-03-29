from abc import ABC
from pprint import pprint
import requests
from datetime import date

from social_core.backends import google, github, apple

from WeatherReminder.tools import generate_code


class GoogleOAuth2(google.GoogleOAuth2, ABC):
    DEFAULT_SCOPE = ['openid', 'email', 'profile']

    def get_user_details(self, response, **kwargs):
        return {'email': response['email'],
                'first_name': response.get('given_name', ' '),
                'last_name': response.get('family_name', ' '),
                'is_active': True
                }

    def get_birthday(self, response):
        url = f'https://people.googleapis.com/v1/people/{response["sub"]}?personFields=birthdays'
        headers = self.auth_headers()
        headers['Authorization'] = f'Bearer {response["access_token"]}'
        try:
            return date(**self.get_json(url, headers=headers)['birthdays'][0]['date'])
        except KeyError:
            return date(year=1970, month=1, day=1)


class GithubOAuth2(github.GithubOAuth2, ABC):
    DEFAULT_SCOPE = ['user:email', 'read:user']

    def get_user_details(self, response):
        return {'email': response['email'],
                'first_name': response.get('name', ' '),
                'last_name': response.get('surname', 'GitHub'),
                'is_active': True
                }


class AppleIdAuth(apple.AppleIdAuth, ABC):
    # TODO: To finish, add auth by AppleID
    pass
