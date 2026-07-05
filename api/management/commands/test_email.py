from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument('to', type=str, help='Recipient email address')

    def handle(self, *args, **options):
        self.stdout.write(f"EMAIL_HOST_USER     : {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD : {'✓ défini' if settings.EMAIL_HOST_PASSWORD else '✗ VIDE'}")
        self.stdout.write(f"EMAIL_HOST          : {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT          : {settings.EMAIL_PORT}")
        self.stdout.write(f"Envoi vers          : {options['to']}")
        self.stdout.write("---")
        try:
            send_mail(
                subject='SafeSchool — Test de configuration email',
                message='Si vous recevez cet email, la configuration SMTP fonctionne correctement.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[options['to']],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('✓ Email envoyé avec succès !'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erreur : {e}'))
