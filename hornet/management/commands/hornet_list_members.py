from logging import getLogger

from hornet import models
from hornet import utils
from .common import ClientCommand

logger = getLogger(__name__)


class Command(ClientCommand):

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=200)
        parser.add_argument("--update-distance", action="store_true")
        parser.add_argument("--method", choices=["near", "favorites"], default="near")

    def handle(self, limit, update_distance, method, *args, **options):
        if update_distance:
            logger.debug("Reset distance")
            models.Member.objects.update(distance=None)
        if method == "near":
            method = self.client.list_near
        elif method == "favorites":
            method = self.client.list_favorites
        else:
            raise AssertionError("Unknown method")
        member_list = utils.increment_list(method, limit)
        if update_distance:
            utils.update_distance(member_list)
            
        self.stderr.write("members: %s\n" % len(member_list))
        for idx, member in enumerate(member_list):
            self.stdout.write(" %s: %s" % (idx, member))
