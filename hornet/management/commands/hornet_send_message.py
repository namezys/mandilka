from logging import getLogger

from hornet import models
from .common import ClientCommand

logger = getLogger(__name__)


class Command(ClientCommand):

    def add_arguments(self, parser):
        parser.add_argument("member_id", type=int)
        parser.add_argument("text")

    def handle(self, member_id, text, *args, **kwargs):
        try:
            member = models.Member.objects.get(pk=member_id)
        except models.Member.DoesNotExist:
            self.stderr.write("Unknown member")
            return

        self.client.send_message(member, text)
