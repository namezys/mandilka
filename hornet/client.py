from logging import getLogger

import requests

from . import models

logger = getLogger(__name__)


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

    def list_near(self, page_num, page_size):
        logger.info("List near profiles: page number %s, page size %s", page_num, page_size)
        return self._list_members(self.BASE_URL + "members/near.json", page_num, page_size)

    def list_favorites(self, page_num, page_size):
        logger.info("List near profiles: page number %s, page size %s", page_num, page_size)
        return self._list_members(self.BASE_URL + "favourites/favourites.json", page_num, page_size)

    def list_message(self, member):
        logger.info("List messages with %s", member)
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

    def send_message(self, member, text):
        logger.info("Send message to %s", member)
        params = {"recipient": member.network_id, "type": "chat", "data": text}
        url = self.BASE_URL + "messages.json"
        response = self.session.post(url, json=params)
        response.raise_for_status()
        logger.debug("Message sent")

    def increment_list(self, method, limit):
        logger.info("Increment download ")
        member_list = []
        page_number = 0
        while len(member_list) < limit:
            logger.debug("Load page: %s", page_number)
            member_list.extend(method(self, page_number, 100))
            logger.debug("Loaded %s members", len(member_list))
            page_number += 1
        return member_list
