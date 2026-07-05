from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('directeur',  'Directeur'),
        ('conseiller', 'Conseiller'),
        ('etudiant',   'Étudiant'),
    ]
    role                 = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    telephone            = models.CharField(max_length=20, blank=True, null=True)
    classe               = models.CharField(max_length=50, blank=True, null=True)
    anonyme              = models.BooleanField(default=False)
    photo                = models.ImageField(upload_to='profiles/', blank=True, null=True)
    identifiant          = models.CharField(max_length=50, unique=True, null=True, blank=True)
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_directeur(self):
        return self.role == 'directeur'

    @property
    def is_conseiller(self):
        return self.role == 'conseiller'

    @property
    def is_etudiant(self):
        return self.role == 'etudiant'


class PasswordResetToken(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token      = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    used       = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Token for {self.user.username}"
