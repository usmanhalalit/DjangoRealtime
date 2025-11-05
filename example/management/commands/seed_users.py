from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with admin users'

    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'admin1@example.com',
                'email': 'admin1@example.com',
                'password': 'admin1@example.com'
            },
            {
                'username': 'admin2@example.com',
                'email': 'admin2@example.com',
                'password': 'admin2@example.com'
            },
            {
                'username': 'admin3@example.com',
                'email': 'admin3@example.com',
                'password': 'admin3@example.com'
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={'email': user_data['email']}
            )

            if not created:
                # Update existing user
                user.email = user_data['email']
                self.stdout.write(
                    self.style.WARNING(f'Updating existing user: {user_data["username"]}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Created new admin user: {user_data["username"]}')
                )

            # Set password and admin privileges for both new and existing users
            user.set_password(user_data['password'])
            user.is_staff = True
            user.is_superuser = True
            user.save()

        self.stdout.write(self.style.SUCCESS('Seed users command completed!'))
