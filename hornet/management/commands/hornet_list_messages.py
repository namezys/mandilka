from logging import getLogger

from hornet import models
from .common import ClientCommand

logger = getLogger(__name__)


class Command(ClientCommand):

    def add_arguments(self, parser):
        parser.add_argument("member_id", type=int)

    def handle(self, member_id, *args, **kwargs):
        try:
            member = models.Member.objects.get(pk=member_id)
        except models.Member.DoesNotExist:
            self.stderr.write("Unknown member")
            return

        result = self.client.list_message(member)
        for message in result:
            print("  ", message)
        self.stderr.write("Total messages: %s" % len(result))
