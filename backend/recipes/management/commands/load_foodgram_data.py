import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, RecipeIngredient

User = get_user_model()

DATA_DIR = Path("/data")


class Command(BaseCommand):
    help = (
        "Loads initial data for the Foodgram project: ingredients, users, recipes, etc."
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting data loading process..."))

        try:
            ingredients_file_path = DATA_DIR / "ingredients.json"
            self.stdout.write(
                self.style.NOTICE(
                    f"Attempting to load ingredients from: {ingredients_file_path}"
                )
            )
            with open(ingredients_file_path, "r", encoding="utf-8") as f:
                ingredients_data = json.load(f)

            loaded_count = 0
            skipped_count = 0
            for item in ingredients_data:
                _, created = Ingredient.objects.get_or_create(
                    name=item["name"], measurement_unit=item["measurement_unit"]
                )
                if created:
                    loaded_count += 1
                else:
                    skipped_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"{loaded_count} new ingredients loaded, {skipped_count} already existed."
                )
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f"{ingredients_file_path} not found. Skipping ingredients."
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading ingredients: {e}"))

        users_data = [
            {
                "username": "admin_user",
                "email": "admin@example.com",
                "password": "TestPassword123",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "test_user1",
                "email": "user1@example.com",
                "password": "TestPassword123",
                "first_name": "Test",
                "last_name": "UserOne",
            },
            {
                "username": "chef_user2",
                "email": "chef2@example.com",
                "password": "TestPassword123",
                "first_name": "Chef",
                "last_name": "Two",
            },
        ]

        created_users_map = {}
        users_created_count = 0
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "is_staff": user_data.get("is_staff", False),
                    "is_superuser": user_data.get("is_superuser", False),
                },
            )
            if created or not user.has_usable_password():
                user.set_password(user_data["password"])
                user.save()
                if created:
                    users_created_count += 1
            created_users_map[user_data["username"]] = user
        self.stdout.write(
            self.style.SUCCESS(f"{users_created_count} new users created/updated.")
        )

        if (
            Ingredient.objects.count() < 3
        ):
            self.stdout.write(
                self.style.WARNING(
                    "Not enough ingredients to create sample recipes. Please load ingredients first."
                )
            )

        recipes_data = [
            {
                "author_username": "test_user1",
                "name": "Простой омлет",
                "image_path": "recipes_images/omelet.jpg",
                "text": "Легкий и быстрый завтрак. Взбейте яйца с молоком, посолите, поперчите. Вылейте на разогретую сковороду с маслом. Готовьте до золотистой корочки.",
                "cooking_time": 10,
                "ingredients": [
                    {"name": "яйца перепелиные", "amount": 20, "measurement_unit": "г"},
                    {"name": "молоко", "amount": 50, "measurement_unit": "мл"},
                ],
            },
            {
                "author_username": "chef_user2",
                "name": "Греческий салат",
                "image_path": "recipes_images/greek_salad.jpg",
                "text": "Свежий и полезный салат. Нарежьте помидоры, огурцы, сладкий перец, красный лук. Добавьте маслины и сыр фета. Заправьте оливковым маслом и орегано.",
                "cooking_time": 15,
                "ingredients": [
                    {
                        "name": "огурцы",
                        "amount": 200,
                        "measurement_unit": "г",
                    },  # Исправлено на Огурцы
                    {
                        "name": "помидоры",
                        "amount": 300,
                        "measurement_unit": "г",
                    },
                    {"name": "сыр адыгейский", "amount": 150, "measurement_unit": "г"},
                    {
                        "name": "маслины без косточек",
                        "amount": 50,
                        "measurement_unit": "г",
                    },
                ],
            },
        ]
        recipes_created_count = 0
        for recipe_data in recipes_data:
            author = created_users_map.get(recipe_data["author_username"])
            if not author:
                self.stdout.write(
                    self.style.WARNING(
                        f"Author '{recipe_data['author_username']}' for recipe '{recipe_data['name']}' not found. Skipping."
                    )
                )
                continue

            recipe_obj, created = Recipe.objects.get_or_create(
                name=recipe_data["name"],
                author=author,
                defaults={
                    "text": recipe_data["text"],
                    "cooking_time": recipe_data["cooking_time"],
                },
            )

            if created:
                recipes_created_count += 1
                for ing_data in recipe_data["ingredients"]:
                    try:
                        ingredient = Ingredient.objects.get(
                            name__iexact=ing_data["name"],
                            measurement_unit__iexact=ing_data["measurement_unit"],
                        )
                        RecipeIngredient.objects.create(
                            recipe=recipe_obj,
                            ingredient=ingredient,
                            amount=ing_data["amount"],
                        )
                    except Ingredient.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Ingredient '{ing_data['name']}' ('{ing_data['measurement_unit']}') not found. Skipping for recipe '{recipe_obj.name}'."
                            )
                        )
                self.stdout.write(
                    self.style.SUCCESS(f"Recipe '{recipe_obj.name}' created.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Recipe '{recipe_obj.name}' already exists. Skipping ingredient creation."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"{recipes_created_count} new recipes created.")
        )
        self.stdout.write(self.style.SUCCESS("Data loading process finished."))
