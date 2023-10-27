import os
import json
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
from tags.models import Tag

class Command(BaseCommand):
    help = 'Load data from JSON files to DB'

    def handle(self, *args, **options):
        self.stdout.write('')
        self.import_tags()
        self.load_ingredients()

    @staticmethod
    def load_ingredients():
        file_path = os.path.join(os.path.dirname(__file__), 'ingredients.json')
        with open(file_path, 'r', encoding='utf-8') as ingredients_file:
            ingredients_data = json.load(ingredients_file)
            for item in ingredients_data:
                Ingredient.objects.get_or_create(name=item['name'], measurement_unit=item['measurement_unit'])

    def import_tags(self):
        data = [
            {"name": "Завтрак", "color": "#00ff00", "slug": "breakfast"},
            {"name": "Обед", "color": "#ffcc00", "slug": "lunch"},
            {"name": "Ужин ", "color": "#004524", "slug": "dinner"},
        ]
        for data_object in data:
            name = data_object.get('name', None)
            color = data_object.get('color', None)
            slug = data_object.get('slug',None)
            try:
                tag, created = (
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug
                    )
                )
                if created:
                    tag.save()
                    display_format = (
                        "\ntag,{},has beed saved."
                        )
                    print(display_format.format(tag))
            except Exception as ex:
                print(str(ex))
                msg = ("\n\nSomething went wrong saving this tag:"
                       "{}\n{}".format(name,str(ex)))
                print(msg)

