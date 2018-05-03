from logging import getLogger

import funcy
import requests

from . import models

logger = getLogger(__name__)

RETRY_NUMBER = 5
RETRY_WAIT = 3


class Client(object):
    BASE_URL = "https://hornet.com/api/v3/"

    def __init__(self, account):
        self.session = requests.Session()
        self.account = account
        self._authenticated = False
        self._check_authentication()

    def _check_authentication(self):
        if self._authenticated:
            return
        if self.account.token:
            logger.debug("Set token from account")
            self.session.headers["Authorization"] = "Hornet " + self.account.token
            self._authenticated = True

    @funcy.retry(RETRY_NUMBER, timeout=RETRY_WAIT, errors=(requests.RequestException, ))
    def set_filter(self, min_age, max_age):
        logger.info("Set filters")
        logger.info("Age filter: %s %s", min_age, max_age)
        age_filter = {"category": "general", "key": "age", "data": {"min": min_age, "max": max_age}}
        filters = {"filters": [{"filter": age_filter}]}
        url = self.BASE_URL + "filters.json"
        response = self.session.post(url, json=filters)
        logger.debug("Response %s", response)
        response.raise_for_status()
        print(response.json())

    def _list_members(self, url, page_num, page_size):
        logger.debug("Request url %s", url)
        response = self.session.get(url, params={"page": page_num, "per_page": page_size})
        logger.debug("Response %s", response)
        response.raise_for_status()
        member_list = response.json()['members']

        result = []
        for member_data in member_list:
            member = models.Member.get(self.account, member_data['member'])
            member.save()
            result.append(member)
        return result

    @funcy.retry(RETRY_NUMBER, timeout=RETRY_WAIT, errors=(requests.RequestException,))
    def list_near(self, page_num, page_size):
        logger.info("List near profiles: page number %s, page size %s", page_num, page_size)
        return self._list_members(self.BASE_URL + "members/near.json", page_num, page_size)

    @funcy.retry(RETRY_NUMBER, timeout=RETRY_WAIT, errors=(requests.RequestException,))
    def list_favorites(self, page_num, page_size):
        logger.info("List near profiles: page number %s, page size %s", page_num, page_size)
        return self._list_members(self.BASE_URL + "favourites/favourites.json", page_num, page_size)

    @funcy.retry(RETRY_NUMBER, timeout=RETRY_WAIT, errors=(requests.RequestException,))
    def list_message(self, member):
        logger.info("List messages with %s", member)
        last_message = models.Message.objects.filter(member=member).order_by('-datetime').first()
        if last_message and last_message.datetime > member.last_online:
            logger.debug("Member was online before last message. Read from DB")
            return models.Message.objects.order_by('-datetime').all()
        url = self.BASE_URL + "messages/" + member.network_id + "/conversation.json"
        logger.debug("Request url %s", url)
        response = self.session.get(url, params={"profile_id": member.network_id,
                                                 "per_page": 1000})
        response.raise_for_status()
        messages_list = response.json()['messages']
        result = []

        for message_data in messages_list:
            message = models.Message.get(member, message_data['message'])
            message.save()
            result.append(message)

        return result

    @funcy.retry(RETRY_NUMBER, timeout=RETRY_WAIT, errors=(requests.RequestException,))
    def send_message(self, member, text):
        logger.info("Send message to %s", member)
        params = {"recipient": member.network_id, "type": "chat", "data": text}
        url = self.BASE_URL + "messages.json"
        response = self.session.post(url, json=params)
        response.raise_for_status()
        logger.debug("Message sent")
