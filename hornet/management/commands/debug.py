from django.core.management.base import BaseCommand
from hornet.client import Client
import pprint


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = Client()
        client.set_token("Si1It2chqp4D2JI8LNa5HnBHrg3qbfpv")
        res = []
        page_number = 0
        while len(res) < 2000:
            res.extend(client.list_near(page_number, 100))
            self.stderr.write("Loaded %s\n" % len(res))
            page_number += 1
        if res[0].distance is None:
            res[0].distance = 0
            res[0].save()
        for idx in range(1, len(res) - 1):
            if res[idx].distance is not None:
                continue
            member = res[idx]
            print("no data at ", idx, ":", member)
            prev_member = res[idx - 1]
            next_member = None
            for idx in range(idx + 1, len(res)):
                if res[idx].distance is not None:
                    print("found next member with distance at", idx)
                    next_member = res[idx]
                    break
            if next_member:
                print("prev", prev_member, "next", next_member, "update", member)
                member.distance = (prev_member.distance + next_member.distance) / 2
                member.save()
            
        pprint.pprint(res)

        self.stderr.write("members: %s\n" % len(res))
