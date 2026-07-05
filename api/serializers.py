from rest_framework import serializers
from accounts.serializers import UserSerializer  # noqa: F401
from .models import Counselor, Report, Appointment, SessionReport, StudentSchedule, Annonce, Activite, SiteContent, Photo, Notification


class CounselorSerializer(serializers.ModelSerializer):
    active_report_count = serializers.IntegerField(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = Counselor
        fields = ['id', 'name', 'specialty', 'gender', 'email',
                  'is_active', 'active_report_count', 'photo_url']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url if obj.photo else None


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Appointment
        fields = ['id', 'date', 'time', 'note', 'status', 'created_at']


class SessionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SessionReport
        fields = ['id', 'summary', 'solutions', 'progress', 'notes', 'created_at']


class ScheduleSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model  = StudentSchedule
        fields = ['id', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class ReportSerializer(serializers.ModelSerializer):
    student_name      = serializers.SerializerMethodField()
    student_classe    = serializers.SerializerMethodField()
    student_email     = serializers.SerializerMethodField()
    student_telephone = serializers.SerializerMethodField()
    counselor_name    = serializers.SerializerMethodField()
    appointment       = AppointmentSerializer(read_only=True)
    session_report    = SessionReportSerializer(read_only=True)
    schedule          = ScheduleSerializer(read_only=True)

    class Meta:
        model  = Report
        fields = ['id', 'numero_dossier', 'report_type', 'description', 'location',
                  'perpetrator', 'perpetrator_classe', 'status', 'is_anonymous', 'photo', 'created_at',
                  'student_name', 'student_classe', 'student_email', 'student_telephone',
                  'counselor_name', 'counselor', 'appointment', 'session_report', 'schedule']

    def get_student_name(self, obj):
        if obj.is_anonymous:
            return 'مجهول الهوية'
        return obj.student.get_full_name() or obj.student.username

    def get_student_classe(self, obj):
        return obj.student.classe or ''

    def get_student_email(self, obj):
        if obj.is_anonymous:
            return None
        return obj.student.email or None

    def get_student_telephone(self, obj):
        if obj.is_anonymous:
            return None
        return obj.student.telephone or None

    def get_counselor_name(self, obj):
        return obj.counselor.name if obj.counselor else None



class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Report
        fields = ['report_type', 'description', 'location',
                  'perpetrator', 'perpetrator_classe', 'is_anonymous', 'photo']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class AnnonceSerializer(serializers.ModelSerializer):
    auteur_name = serializers.SerializerMethodField()
    photo_url   = serializers.SerializerMethodField()

    class Meta:
        model  = Annonce
        fields = ['id', 'titre', 'contenu', 'categorie', 'publie',
                  'auteur_name', 'photo', 'photo_url', 'created_at', 'updated_at']

    def get_auteur_name(self, obj):
        if not obj.auteur:
            return ''
        return obj.auteur.get_full_name() or obj.auteur.username

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url if obj.photo else None


class ActiviteSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = Activite
        fields = ['id', 'titre', 'description', 'date', 'heure',
                  'lieu', 'responsable', 'statut', 'photo', 'photo_url', 'created_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url if obj.photo else None


class SiteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SiteContent
        fields = ['id', 'key', 'label', 'value', 'content_type', 'updated_at']


class PhotoSerializer(serializers.ModelSerializer):
    image_url      = serializers.SerializerMethodField()
    subject_label  = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()

    class Meta:
        model  = Photo
        fields = ['id', 'category', 'category_label', 'title', 'image', 'image_url',
                  'description', 'subject', 'subject_label', 'order', 'created_at']
        extra_kwargs = {'image': {'required': True, 'write_only': False}}

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

    def get_subject_label(self, obj):
        return obj.get_subject_display() if obj.subject else ''

    def get_category_label(self, obj):
        return obj.get_category_display()



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'message', 'type', 'is_read', 'created_at']
