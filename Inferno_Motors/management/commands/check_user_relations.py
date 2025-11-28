# Inferno_Motors/management/commands/check_user_relations.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models.deletion import Collector
from django.db import DEFAULT_DB_ALIAS
# Import your app model using the app label (not prefixed by project name)
from car_site.Inferno_Motors.models import *


class Command(BaseCommand):
    help = "Show what models reference a user and what would be deleted if the user is removed."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to inspect')

    def handle(self, *args, **options):
        email = options['email']
        try:
            u = userdetails.objects.get(email=email)
        except userdetails.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User not found: {email}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Inspecting relations for user: {email} (id={u.id})\n"))

        found_any = False
        for model in apps.get_models():
            for field in model._meta.get_fields():
                remote = getattr(field, 'remote_field', None)
                if not remote:
                    continue
                rel_model = remote.model
                # Compare by model object or by name to handle string references
                if rel_model == userdetails or getattr(rel_model, '__name__', '') == userdetails.__name__:
                    kwargs = {field.name: u}
                    qs = model.objects.filter(**kwargs)
                    cnt = qs.count()
                    if cnt:
                        found_any = True
                        self.stdout.write(f" -> {model._meta.label} has {cnt} object(s) referencing this user via field '{field.name}'")
                        for inst in qs[:50]:
                            self.stdout.write(f"    - {repr(inst)}")

        if not found_any:
            self.stdout.write(self.style.WARNING("No direct FK/OneToOne references to this user found."))

        # Show the Collector view (what Django would delete)
        collector = Collector(using=DEFAULT_DB_ALIAS)
        collector.collect([u])
        self.stdout.write("\nCollector would delete these model counts:")
        for model, instances in collector.data.items():
            self.stdout.write(f" - {model._meta.label}: {len(instances)}")

        self.stdout.write(self.style.SUCCESS("\nInspection complete."))
