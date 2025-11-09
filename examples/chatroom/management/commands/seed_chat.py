from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from djangorealtime.publisher import publish_global


class Command(BaseCommand):
    help = 'Seeds the database with test users and chat messages (via events)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create test users
        usernames = ['coolkid99', 'sk8erboi', 'princesspeach', 'hackerman', 'radgal2000']

        users = []
        for username in usernames:
            user, created = User.objects.get_or_create(username=username)
            users.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: {username}'))
            else:
                self.stdout.write(f'  User already exists: {username}')

        # Create sample messages by publishing events
        messages = [
            (users[0], "Hey everyone! Welcome to my rad chatroom!"),
            (users[1], "This is totally awesome dude!"),
            (users[2], "ASL? jk lol"),
            (users[3], "I'm in... *puts on sunglasses*"),
            (users[4], "Anyone remember when we had to use dial-up?"),
            (users[0], "brb mom's on the phone"),
            (users[1], "LOL same! Can't wait for DSL"),
            (users[2], "Check out my GeoCities page! It has animated GIFs!"),
            (users[3], "I just downloaded Winamp. It really whips the llama's..."),
            (users[4], "Y2K is coming! Better stock up on supplies!"),
        ]

        for user, message_text in messages:
            # Publish chat message event (will be stored automatically)
            publish_global('chat_message', {
                'username': user.username,
                'message': message_text,
                'timestamp': datetime.now().isoformat(),
            })
            self.stdout.write(self.style.SUCCESS(f'✓ Published message from {user.username}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!'))
        self.stdout.write(f'  Created {len(users)} users')
        self.stdout.write(f'  Published {len(messages)} chat events')
