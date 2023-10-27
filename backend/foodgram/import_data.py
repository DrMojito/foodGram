import os
import json
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
from tags.models import Tag
from foodgram.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Load data from JSON files to DB'

    def handle(self, *args, **options):
        self.stdout.write('')
        self.load_tags()
        self.load_ingredients()

    @staticmethod
    def load_ingredients():
        with open(os.path.join(BASE_DIR, r'C:\Dev\diplom\foodgram-project-react\data\ingredients.json'), 'r', encoding='utf-8') as ingredients_file:
            ingredients_data = json.load(ingredients_file)
            for item in ingredients_data:
                Ingredient.objects.get_or_create(name=item['name'], measurement_unit=item['measurement_unit'])

    @staticmethod
    def load_tags():
        with open(os.path.join(BASE_DIR, r'C:\Dev\diplom\foodgram-project-react\data\tags.json'), 'r', encoding='utf-8') as tags_file:
            tags_data = json.load(tags_file)
            for item in tags_data:
                Tag.objects.get_or_create(name=item['name'], color=item['color'], slug=item['slug'])