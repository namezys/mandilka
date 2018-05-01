from logging import getLogger

from django.db import models
from django.utils import dateparse

logger = getLogger(__name__)

FIELD_LENGTH = 64


class Account(models.Model):
    username = models.CharField(max_length=FIELD_LENGTH, null=False, blank=False)
    token = models.CharField(max_length=FIELD_LENGTH)

    @classmethod
    def get_account(cls, username):
        try:
            return cls.objects.get(username__iexact=username)
        except cls.DoesNotExist:
            return None


class Member(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT, null=False, blank=False)
    network_id = models.CharField(max_length=FIELD_LENGTH, null=False, blank=False)

    name = models.CharField(max_length=FIELD_LENGTH, null=True, blank=True)
    username = models.CharField(max_length=FIELD_LENGTH, null=False, blank=False)
    age = models.IntegerField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "member #{0.pk}:{0.network_id}: {0.name} (age {0.age}) at {0.distance}".format(self)

    @classmethod
    def find(cls, account, network_id):
        logger.debug("Find member %s", network_id)
        try:
            return cls.objects.get(account=account, network_id=network_id)
        except cls.DoesNotExist:
            return None

    def update(self, network_data):
        logger.debug("Update %s", self)
        self.network_id = str(network_data['id'])
        self.name = network_data['display_name']
        self.username = network_data['account']['username']
        self.age = network_data['age']
        self.distance = network_data.get('distance')
        self.last_online = dateparse.parse_datetime(network_data['last_online'])

    @classmethod
    def get(cls, account, network_data):
        network_id = network_data['id']
        member = cls.find(account, network_id)
        if not member:
            member = cls(account=account, network_id=network_id)
        member.update(network_data)
        return member


class Message(models.Model):
    TYPE_CHAT = "chat"
    TYPE_PRIVATE_REQUEST = "private_request"
    TYPE_PRIVATE_RESPONSE = "private_response"
    TYPE_STICKER = "sticker"
    TYPE_PHOTO = "share_photo"
    TYPE_LOCATION = "location"
    TYPES = [TYPE_CHAT, TYPE_PRIVATE_REQUEST, TYPE_STICKER, TYPE_PHOTO, TYPE_LOCATION]
    
    network_id = models.CharField(max_length=FIELD_LENGTH, null=False, blank=False)

    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=False, blank=False)
    text = models.TextField(null=False, blank=False)
    datetime = models.DateTimeField(null=False, blank=False)
    type = models.CharField(max_length=FIELD_LENGTH, choices=zip(TYPES, TYPES))
    is_incoming = models.BooleanField()

    def __str__(self):
        return "message #{0.pk}:{0.network_id}: |{0.type}{direction}| {0.text} at {0.datetime}"\
            .format(self, direction=">" if self.is_incoming else "<")

    @classmethod
    def find(cls, network_id):
        logger.debug("Find message %s", network_id)
        try:
            return cls.objects.get(network_id=network_id)
        except cls.DoesNotExist:
            return None

    def update(self, member, network_data):
        logger.debug("Update %s", self)
        self.network_id = str(network_data['id'])
        self.member = member
        message_type = network_data['type']
        is_incoming = (str(network_data['sender']) == member.network_id)
        
        if message_type == 'chat':
            self.type = self.TYPE_CHAT
            assert self.type in self.TYPES, "invalid type %r" % self.type
            self.text = network_data['data']
        elif message_type == 'permission_request':
            assert network_data['data']['permission']['permission_type'] == 'private_photo_access'
            self.type = self.TYPE_PRIVATE_REQUEST
            self.text = "images"
        elif message_type == 'permission_response':
            assert network_data['data']['permission']['permission_type'] == 'private_photo_access'
            self.type = self.TYPE_PRIVATE_RESPONSE
            self.text = "images"
        elif message_type == "sticker":
            self.type = self.TYPE_STICKER
            self.text = network_data['data']['sticker']['reference']
        elif message_type == "share_photo":
            self.type = self.TYPE_PHOTO
            self.text = "image"
        elif message_type == "location":
            self.type = self.TYPE_LOCATION
            self.text = "location"
        else:
            print(network_data)
            raise AssertionError("unknown type")

        self.is_incoming = is_incoming
        self.datetime = dateparse.parse_datetime(network_data['created_at'])
            
        return self

    @classmethod
    def get(cls, member, network_data):
        network_id = network_data['id']
        instance = cls.find(network_id)
        if not instance:
            instance = cls(network_id=network_id)
        instance.update(member, network_data)
        return instance
