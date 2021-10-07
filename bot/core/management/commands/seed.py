from django.core.management.base import BaseCommand

from core.models import Tag
from core.management.commands.tags_seeding_data import tag_list

def tags_seeding(tags):
    for tag in tags:
        Tag.objects.get_or_create(name=tag)

class Command(BaseCommand):
    help = 'Seeding'

    def handle(self, *args, **options):
        tags_seeding(tags=tag_list)