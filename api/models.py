from django.db import models
from django.db.models import Max
from accounts.models import User


class Counselor(models.Model):
    GENDER_CHOICES = [('male', 'ذكر'), ('female', 'أنثى')]

    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='counselor_profile')
    name      = models.CharField(max_length=150)
    specialty = models.CharField(max_length=150, blank=True)
    gender    = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')
    email     = models.EmailField(blank=True)
    photo     = models.ImageField(upload_to='counselors/photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def active_report_count(self):
        return self.reports.exclude(status='تم الحل').count()


class Report(models.Model):
    STATUS_CHOICES = [
        ('جديد',          'جديد'),
        ('قيد المعالجة',  'قيد المعالجة'),
        ('موعد محدد',     'موعد محدد'),
        ('تم الحل',       'تم الحل'),
    ]
    TYPE_CHOICES = [
        ('التحرش الجسدي',    'التحرش الجسدي'),
        ('التحرش اللفظي',    'التحرش اللفظي'),
        ('التحرش الإلكتروني','التحرش الإلكتروني'),
        ('العنف اللفظي أو التهديد', 'العنف اللفظي أو التهديد'),
        ('الإقصاء الاجتماعي','الإقصاء الاجتماعي'),
        ('التمييز',          'التمييز'),
        ('التمييز العرقي',  'التمييز العرقي'),
        ('التمييز الجنسي',  'التمييز الجنسي'),
        ('التمييز الديني',  'التمييز الديني'),
        ('التحرش الجنسي',   'التحرش الجنسي'),
        ('أخرى',            'أخرى'),
    ]

    student        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    counselor      = models.ForeignKey(Counselor, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    numero_dossier = models.PositiveIntegerField(default=0, db_index=True)
    report_type    = models.CharField(max_length=100, choices=TYPE_CHOICES)
    description    = models.TextField()
    location       = models.CharField(max_length=200, blank=True)
    perpetrator        = models.CharField(max_length=200, blank=True)
    perpetrator_classe = models.CharField(max_length=100, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='جديد')
    is_anonymous   = models.BooleanField(default=False)
    photo          = models.ImageField(upload_to='reports/photos/', blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Attribuer un numéro de dossier séquentiel à la création
        if not self.pk and self.numero_dossier == 0:
            max_num = Report.objects.aggregate(m=Max('numero_dossier'))['m'] or 0
            self.numero_dossier = max_num + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.numero_dossier} — {self.report_type} ({self.status})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('مقترح', 'مقترح'),
        ('مقبول', 'مقبول'),
        ('مرفوض', 'مرفوض'),
    ]
    report     = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='appointment')
    date       = models.DateField()
    time       = models.TimeField()
    note       = models.TextField(blank=True)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='مقترح')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rendez-vous #{self.report.pk} — {self.date} {self.time}"


class StudentSchedule(models.Model):
    report      = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='schedule')
    file        = models.FileField(upload_to='schedules/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emploi du temps — Dossier #{self.report.pk}"


class SessionReport(models.Model):
    PROGRESS_CHOICES = [
        ('en_cours',     'En cours de suivi'),
        ('amelioration', 'Amélioration notable'),
        ('resolu',       'Résolu'),
    ]
    report     = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='session_report')
    counselor  = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='session_reports')
    summary    = models.TextField(blank=True)
    solutions  = models.TextField(blank=True)
    progress   = models.CharField(max_length=20, choices=PROGRESS_CHOICES, default='en_cours')
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rapport séance — Dossier #{self.report.pk}"


class Annonce(models.Model):
    CATEGORIE_CHOICES = [
        ('info',      'Information'),
        ('urgence',   'Urgence'),
        ('evenement', 'Événement'),
        ('alerte',    'Alerte'),
    ]
    titre      = models.CharField(max_length=200)
    contenu    = models.TextField()
    categorie  = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='info')
    publie     = models.BooleanField(default=True)
    auteur     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='annonces')
    photo      = models.ImageField(upload_to='annonces/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.titre


class Activite(models.Model):
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours',  'En cours'),
        ('terminee',  'Terminée'),
        ('annulee',   'Annulée'),
    ]
    titre       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date        = models.DateField()
    heure       = models.TimeField(blank=True, null=True)
    lieu        = models.CharField(max_length=200, blank=True)
    responsable = models.CharField(max_length=150, blank=True)
    statut      = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')
    photo       = models.ImageField(upload_to='activites/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.titre


class Photo(models.Model):
    CATEGORY_CHOICES = [
        ('professeurs', 'Professeurs'),
        ('activites',   'Activités scolaires'),
        ('accueil',     'Diaporama Accueil'),
    ]
    SUBJECT_CHOICES = [
        ('education_islamique', 'Éducation islamique'),
        ('histoire_geo',        'Histoire-Géographie'),
        ('mathematiques',       'Mathématiques'),
        ('physique',            'Physique'),
        ('francais',            'Français'),
        ('informatique',        'Informatique'),
        ('anglais',             'Anglais'),
        ('sport',               'Sport'),
        ('svt',                 'SVT'),
        ('autre',               'Autre'),
    ]
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title       = models.CharField(max_length=200)
    image       = models.ImageField(upload_to='photos/')
    description = models.TextField(blank=True)
    subject     = models.CharField(max_length=30, choices=SUBJECT_CHOICES, blank=True)  # pour professeurs
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('appointment', 'Rendez-vous'),
        ('update',      'Mise à jour'),
        ('info',        'Information'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message    = models.TextField()
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif {self.user.username} — {self.message[:40]}"


class SiteContent(models.Model):
    TYPE_CHOICES = [
        ('text',  'Texte'),
        ('image', 'Image'),
        ('html',  'HTML'),
    ]
    key          = models.CharField(max_length=100, unique=True)
    label        = models.CharField(max_length=200, blank=True)
    value        = models.TextField(blank=True)
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key
