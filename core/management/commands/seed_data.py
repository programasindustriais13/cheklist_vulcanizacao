from django.core.management.base import BaseCommand
from core.models import User, Machine

class Command(BaseCommand):
    help = 'Seeds database with default users and machines for testing.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Create Superuser (Admin)
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword',
                specialty='Lider',
                first_name='Admin',
                last_name='System'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / adminpassword'))
        else:
            self.stdout.write('Superuser "admin" already exists.')

        # 2. Create Inspector User
        if not User.objects.filter(username='inspector').exists():
            inspector_user = User.objects.create_user(
                username='inspector',
                email='inspector@example.com',
                password='inspectorpassword',
                specialty='Eletromecânico',
                first_name='João',
                last_name='Silva'
            )
            self.stdout.write(self.style.SUCCESS('Inspector user created: inspector / inspectorpassword'))
        else:
            self.stdout.write('Inspector user "inspector" already exists.')

        # 3. Create Default Machines
        default_machines = [
            {'name': 'Prensa Vulcanizadora 01', 'description': 'Prensa Hidráulica de Vulcanização - Linha A'},
            {'name': 'Prensa Vulcanizadora 02', 'description': 'Prensa Hidráulica de Vulcanização - Linha B'},
            {'name': 'Injetora de Borracha 05', 'description': 'Injetora de Borracha CNC - Setor Sul'},
            {'name': 'Torno Mecânico ROMI', 'description': 'Torno Universal ROMI T-240'},
        ]

        for m in default_machines:
            machine, created = Machine.objects.get_or_create(
                name=m['name'],
                defaults={'description': m['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Machine '{machine.name}' created."))
            else:
                self.stdout.write(f"Machine '{machine.name}' already exists.")

        self.stdout.write(self.style.SUCCESS('Database seeding finished successfully!'))
