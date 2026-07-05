from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
import secrets
import string


def safe_send_mail(**kwargs):
    """Send email and return True on success, False on failure."""
    try:
        send_mail(**kwargs)
        return True
    except Exception as e:
        import sys
        print(f"[SafeSchool EMAIL ERROR] {e}", file=sys.stderr)
        return False


def email_html(title, body, color='#0d9488'):
    """Return a clean, branded HTML email string."""
    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:32px 16px;">
    <table width="560" cellpadding="0" cellspacing="0" style="background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
      <!-- Header -->
      <tr><td style="background:{color};padding:24px 32px;">
        <p style="margin:0;font-size:1.3rem;font-weight:900;color:white;">🛡️ SafeSchool</p>
        <p style="margin:6px 0 0;font-size:1rem;color:rgba(255,255,255,0.85);font-weight:600;">{title}</p>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:28px 32px;color:#334155;font-size:0.95rem;line-height:1.7;">
        {body}
      </td></tr>
      <!-- Footer -->
      <tr><td style="padding:16px 32px;background:#f8fafc;border-top:1px solid #e2e8f0;text-align:center;">
        <p style="margin:0;font-size:0.78rem;color:#94a3b8;">
          Cet e-mail a été envoyé automatiquement par SafeSchool. Ne pas répondre directement.
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""
import csv, io, random, string
from accounts.models import User
from accounts.serializers import UserSerializer
from .models import Counselor, Report, Appointment, StudentSchedule, Annonce, Activite, SiteContent, Photo, Notification
from .serializers import (CounselorSerializer, ReportSerializer,
                           ReportCreateSerializer, AppointmentSerializer,
                           SessionReportSerializer, ScheduleSerializer,
                           AnnonceSerializer, ActiviteSerializer, SiteContentSerializer,
                           PhotoSerializer, NotificationSerializer)


def gen_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def push_notif(user, message, type='info'):
    Notification.objects.create(user=user, message=message, type=type)


class IsDirecteur(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'directeur'


class IsConseiller(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'conseiller'


# ── Reports ──────────────────────────────────────────────────────────────────

class ReportListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'directeur':
            qs = Report.objects.all()
        elif user.role == 'conseiller':
            qs = Report.objects.filter(counselor__user=user)
        else:
            qs = Report.objects.filter(student=user)
        return Response(ReportSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        if request.user.role != 'etudiant':
            return Response({'error': 'Seuls les élèves peuvent soumettre un signalement.'}, status=403)
        s = ReportCreateSerializer(data=request.data, context={'request': request})
        if s.is_valid():
            report = s.save()
            return Response(ReportSerializer(report, context={'request': request}).data, status=201)
        return Response(s.errors, status=400)


class ReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return None

    def get(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(status=404)
        return Response(ReportSerializer(report, context={'request': request}).data)

    def delete(self, request, pk):
        if request.user.role != 'directeur':
            return Response(status=403)
        report = self.get_object(pk)
        if report:
            report.delete()
        return Response(status=204)


class AssignCounselorView(APIView):
    permission_classes = [IsDirecteur]

    def post(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
            counselor = Counselor.objects.get(pk=request.data.get('counselor_id'))
        except (Report.DoesNotExist, Counselor.DoesNotExist):
            return Response({'error': 'Signalement ou conseiller introuvable.'}, status=404)

        report.counselor = counselor
        report.status    = 'قيد المعالجة'
        report.save()

        student_name = report.student.get_full_name() or report.student.username

        num = report.numero_dossier

        # Email → student
        if report.student.email:
            safe_send_mail(
                subject=f'SafeSchool — Un conseiller a été assigné à votre dossier #{num}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[report.student.email],
                message='',
                fail_silently=True,
                html_message=email_html(
                    title='Un conseiller a été assigné à votre dossier',
                    color='#1d4ed8',
                    body=f"""
                    <p>Bonjour <strong>{student_name}</strong>,</p>
                    <p>Le conseiller <strong>{counselor.name}</strong> a été assigné pour suivre votre dossier
                    <strong>#{num}</strong>.</p>
                    <p>Il/Elle vous contactera prochainement pour fixer une date de séance.</p>
                    """
                )
            )

        # Email → counselor
        if counselor.email:
            safe_send_mail(
                subject=f'SafeSchool — Nouveau dossier assigné #{num}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[counselor.email],
                message='',
                fail_silently=True,
                html_message=email_html(
                    title=f'Nouveau dossier assigné — #{num}',
                    color='#0d9488',
                    body=f"""
                    <p>Bonjour <strong>{counselor.name}</strong>,</p>
                    <p>Un nouveau dossier vous a été confié :</p>
                    <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:0.95rem;">
                      <tr><td style="padding:10px 12px;background:#f8fafc;font-weight:700;width:40%;">N° dossier</td><td style="padding:10px 12px;">#{num}</td></tr>
                      <tr><td style="padding:10px 12px;background:#f1f5f9;font-weight:700;">Type</td><td style="padding:10px 12px;">{report.report_type}</td></tr>
                      <tr><td style="padding:10px 12px;background:#f8fafc;font-weight:700;">Élève</td><td style="padding:10px 12px;">{student_name}</td></tr>
                      <tr><td style="padding:10px 12px;background:#f1f5f9;font-weight:700;">Classe</td><td style="padding:10px 12px;">{report.student.classe or '—'}</td></tr>
                    </table>
                    <p>Connectez-vous à la plateforme pour consulter les détails et proposer un rendez-vous.</p>
                    """
                )
            )

        return Response(ReportSerializer(report, context={'request': request}).data)


class AppointmentView(APIView):
    permission_classes = [IsConseiller]

    def post(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response(status=404)

        s = AppointmentSerializer(data=request.data)
        if s.is_valid():
            Appointment.objects.filter(report=report).delete()
            appt = s.save(report=report)
            report.status = 'موعد محدد'
            report.save()

            # Email → student
            student_name = report.student.get_full_name() or report.student.username
            if report.student.email:
                note_html = f"<p style='color:#374151;margin-top:8px;'>{appt.note}</p>" if appt.note else ""
                safe_send_mail(
                    subject=f'SafeSchool — Rendez-vous proposé pour votre dossier #{report.numero_dossier}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[report.student.email],
                    message='',
                    fail_silently=True,
                    html_message=email_html(
                        title='Rendez-vous proposé',
                        color='#0d9488',
                        body=f"""
                        <p>Bonjour <strong>{student_name}</strong>,</p>
                        <p>Votre conseiller vous propose un rendez-vous pour la séance de suivi :</p>
                        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:18px;margin:16px 0;text-align:center;">
                          <p style="font-size:1.25rem;font-weight:900;color:#166534;margin:0;">📅 {appt.date} &nbsp;·&nbsp; {str(appt.time)[:5]}</p>
                          {note_html}
                        </div>
                        <p>Connectez-vous à la plateforme pour <strong>accepter ou refuser</strong> ce rendez-vous.</p>
                        """
                    )
                )
            push_notif(
                report.student,
                f'📅 Un rendez-vous vous a été proposé pour le dossier #{report.numero_dossier} : {appt.date} à {str(appt.time)[:5]}.',
                type='appointment'
            )
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class SessionReportView(APIView):
    permission_classes = [IsConseiller]

    def post(self, request, pk):
        try:
            report = Report.objects.get(pk=pk, counselor__user=request.user)
        except Report.DoesNotExist:
            return Response(status=404)

        s = SessionReportSerializer(data=request.data)
        if s.is_valid():
            # Delete existing session report if present (counselor can overwrite)
            from .models import SessionReport
            SessionReport.objects.filter(report=report).delete()
            s.save(report=report, counselor=request.user.counselor_profile)
            report.status = 'تم الحل'
            report.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


# ── Counselors ────────────────────────────────────────────────────────────────

class CounselorListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Counselor.objects.all()
        return Response(CounselorSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        if request.user.role != 'directeur':
            return Response(status=403)
        data = request.data

        # Email obligatoire
        email = data.get('email', '').strip()
        if not email:
            return Response({'error': "L'adresse e-mail du conseiller est obligatoire pour l'envoi des identifiants."}, status=400)

        # Check duplicate name
        if Counselor.objects.filter(name__iexact=data.get('name', '')).exists():
            return Response({'error': 'Un conseiller avec ce nom existe déjà.'}, status=400)

        # Check gender limits
        gender = data.get('gender', 'female')
        if gender == 'male' and Counselor.objects.filter(gender='male').count() >= 1:
            return Response({'error': 'Maximum 1 conseiller masculin autorisé.'}, status=400)
        if gender == 'female' and Counselor.objects.filter(gender='female').count() >= 2:
            return Response({'error': 'Maximum 2 conseillères féminines autorisées.'}, status=400)

        # Check duplicate username (global — unique across all roles)
        if User.objects.filter(username=data.get('username', '')).exists():
            return Response({'error': "Ce nom d'utilisateur est déjà utilisé."}, status=400)

        # Check duplicate email (global — unique across all roles)
        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': "Cette adresse e-mail est déjà utilisée par un autre compte."}, status=400)

        # Auto-generate a secure password (12 chars: letters + digits + symbols)
        alphabet = string.ascii_letters + string.digits + '!@#$%'
        auto_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        user = User.objects.create_user(
            username   = data['username'],
            password   = auto_password,
            first_name = data.get('name', ''),
            email      = email,
            role       = 'conseiller',
        )
        counselor = Counselor.objects.create(
            user      = user,
            name      = data.get('name', ''),
            specialty = data.get('specialty', ''),
            gender    = gender,
            email     = email,
        )

        # Send credentials email to counselor
        director_name = request.user.get_full_name() or request.user.username
        email_sent = safe_send_mail(
            subject='SafeSchool — Vos identifiants de connexion',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            message='',
            fail_silently=True,
            html_message=email_html(
                title='Bienvenue sur SafeSchool',
                color='#0d9488',
                body=f"""
                <p>Bonjour <strong>{counselor.name}</strong>,</p>
                <p>Le directeur <strong>{director_name}</strong> vient de créer votre compte conseiller
                   sur la plateforme <strong>SafeSchool</strong>. Vous pouvez vous connecter dès maintenant
                   avec les identifiants générés automatiquement ci-dessous :</p>
                <table style="width:100%;border-collapse:collapse;margin:20px 0;border-radius:12px;overflow:hidden;font-size:0.95rem;">
                  <tr>
                    <td style="padding:14px 18px;background:#f0fdfa;font-weight:700;width:40%;">Nom d'utilisateur</td>
                    <td style="padding:14px 18px;background:#f8fafc;font-family:monospace;font-size:1.05rem;letter-spacing:0.05em;">{data['username']}</td>
                  </tr>
                  <tr>
                    <td style="padding:14px 18px;background:#f0fdfa;font-weight:700;">Mot de passe</td>
                    <td style="padding:14px 18px;background:#f8fafc;font-family:monospace;font-size:1.05rem;letter-spacing:0.08em;">{auto_password}</td>
                  </tr>
                </table>
                <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 18px;margin-bottom:16px;">
                  <p style="margin:0;color:#92400e;font-size:0.88rem;">
                    ⚠️ <strong>Important :</strong> Ce mot de passe a été généré automatiquement par le système.
                    Veuillez le modifier dès votre première connexion depuis la page <em>Mon profil</em>.
                  </p>
                </div>
                <p>Si vous avez des questions, contactez directement le directeur de votre établissement.</p>
                """
            )
        )

        data_out = CounselorSerializer(counselor, context={'request': request}).data
        data_out['email_sent'] = email_sent
        return Response(data_out, status=201)


class CounselorDetailView(APIView):
    permission_classes = [IsDirecteur]

    def delete(self, request, pk):
        try:
            counselor = Counselor.objects.get(pk=pk)
            counselor.user.delete()
            return Response(status=204)
        except Counselor.DoesNotExist:
            return Response(status=404)


class CounselorProfileView(APIView):
    """Counselor can view and update their own profile + upload photo."""
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            counselor = request.user.counselor_profile
        except Exception:
            return Response(status=404)
        return Response(CounselorSerializer(counselor, context={'request': request}).data)

    def patch(self, request):
        try:
            counselor = request.user.counselor_profile
        except Exception:
            return Response(status=404)
        if 'photo' in request.FILES:
            counselor.photo = request.FILES['photo']
        if 'specialty' in request.data:
            counselor.specialty = request.data['specialty']
        counselor.save()
        return Response(CounselorSerializer(counselor, context={'request': request}).data)


# ── Students ──────────────────────────────────────────────────────────────────

class StudentListView(APIView):
    permission_classes = [IsDirecteur]

    def get(self, request):
        qs = User.objects.filter(role='etudiant').order_by('-date_joined')
        return Response(UserSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        data = request.data
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if not username or not password:
            return Response({'error': "Nom d'utilisateur et mot de passe requis."}, status=400)
        if len(password) < 6:
            return Response({'error': 'Le mot de passe doit contenir au moins 6 caractères.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': "Ce nom d'utilisateur est déjà utilisé."}, status=400)
        user = User.objects.create_user(
            username   = username,
            password   = password,
            first_name = data.get('first_name', '').strip(),
            last_name  = data.get('last_name', '').strip(),
            email      = data.get('email', '').strip(),
            telephone  = data.get('telephone', '').strip(),
            classe     = data.get('classe', '').strip(),
            role       = 'etudiant',
            is_active  = True,
        )
        return Response(UserSerializer(user).data, status=201)

    def delete(self, request):
        """DELETE /api/students/?niveau=1APIC — supprime tous les élèves d'un niveau."""
        niveau = request.query_params.get('niveau', '').strip()
        if niveau:
            User.objects.filter(role='etudiant', classe__startswith=niveau).delete()
        else:
            User.objects.filter(role='etudiant').delete()
        return Response(status=204)


class ActivateStudentView(APIView):
    permission_classes = [IsDirecteur]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, role='etudiant')
            user.is_active = not user.is_active
            user.save()
            return Response({'is_active': user.is_active})
        except User.DoesNotExist:
            return Response(status=404)


class StudentDetailView(APIView):
    permission_classes = [IsDirecteur]

    def delete(self, request, pk):
        try:
            User.objects.filter(pk=pk, role='etudiant').delete()
            return Response(status=204)
        except Exception:
            return Response(status=404)


# ── Stats ─────────────────────────────────────────────────────────────────────

class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'directeur':
            reports = Report.objects.all()
        elif request.user.role == 'conseiller':
            reports = Report.objects.filter(counselor__user=request.user)
        else:
            reports = Report.objects.filter(student=request.user)

        needs_appt = reports.filter(status='قيد المعالجة').count()
        # also count rejected appointments that need rescheduling
        needs_appt += reports.filter(
            status='موعد محدد', appointment__status='مرفوض'
        ).count()

        return Response({
            'total':       reports.count(),
            'new':         reports.filter(status='جديد').count(),
            'in_progress': reports.filter(status='قيد المعالجة').count(),
            'appointed':   reports.filter(status='موعد محدد').count(),
            'resolved':    reports.filter(status='تم الحل').count(),
            'students':    User.objects.filter(role='etudiant').count(),
            'pending':     User.objects.filter(role='etudiant', is_active=False).count(),
            'needs_appt':  needs_appt,
        })


# ── Appointment respond (student) ─────────────────────────────────────────────

class AppointmentRespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'etudiant':
            return Response(status=403)
        try:
            report = Report.objects.get(pk=pk, student=request.user)
        except Report.DoesNotExist:
            return Response(status=404)

        if not hasattr(report, 'appointment'):
            return Response({'error': 'Aucun rendez-vous proposé pour ce dossier.'}, status=400)

        action = request.data.get('action')
        counselor = report.counselor
        student_name = request.user.get_full_name() or request.user.username

        if action == 'accept':
            report.appointment.status = 'مقبول'
            report.appointment.save()
            # Email → counselor
            if counselor and counselor.email:
                safe_send_mail(
                    subject=f'SafeSchool — Rendez-vous accepté — Dossier #{report.numero_dossier}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[counselor.email],
                    message='',
                    fail_silently=True,
                    html_message=email_html(
                        title='Rendez-vous accepté ✅',
                        color='#16a34a',
                        body=f"""
                        <p>L'élève <strong>{student_name}</strong> a <strong>accepté</strong> le rendez-vous proposé pour le dossier <strong>#{report.numero_dossier}</strong>.</p>
                        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:18px;margin:16px 0;text-align:center;">
                          <p style="font-size:1.2rem;font-weight:900;color:#166534;margin:0;">
                            ✅ {report.appointment.date} &nbsp;·&nbsp; {str(report.appointment.time)[:5]}
                          </p>
                        </div>
                        <p>Le rendez-vous est confirmé. Préparez la séance de suivi.</p>
                        """
                    )
                )
            if counselor:
                push_notif(
                    counselor.user,
                    f'✅ {student_name} a accepté le rendez-vous du dossier #{report.numero_dossier}.',
                    type='appointment'
                )
        elif action == 'reject':
            report.appointment.status = 'مرفوض'
            report.appointment.save()
            report.status = 'قيد المعالجة'
            report.save()
            # Email → counselor
            if counselor and counselor.email:
                safe_send_mail(
                    subject=f'SafeSchool — Rendez-vous refusé — Dossier #{report.numero_dossier}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[counselor.email],
                    message='',
                    fail_silently=True,
                    html_message=email_html(
                        title='Rendez-vous refusé',
                        color='#dc2626',
                        body=f"""
                        <p>L'élève <strong>{student_name}</strong> a <strong>refusé</strong> le rendez-vous proposé pour le dossier <strong>#{report.numero_dossier}</strong>.</p>
                        <p>Connectez-vous à la plateforme pour proposer un nouveau créneau.<br>
                        L'élève peut également partager son emploi du temps pour vous aider à trouver un horaire adapté.</p>
                        """
                    )
                )
            if counselor:
                push_notif(
                    counselor.user,
                    f'❌ {student_name} a refusé le rendez-vous du dossier #{report.numero_dossier}.',
                    type='appointment'
                )
        else:
            return Response({'error': 'Action invalide.'}, status=400)

        return Response(AppointmentSerializer(report.appointment).data)


# ── Student schedule upload ────────────────────────────────────────────────────

class StudentScheduleView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, pk):
        if request.user.role != 'etudiant':
            return Response(status=403)
        try:
            report = Report.objects.get(pk=pk, student=request.user)
        except Report.DoesNotExist:
            return Response(status=404)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'Veuillez joindre un fichier.'}, status=400)

        StudentSchedule.objects.filter(report=report).delete()
        schedule = StudentSchedule.objects.create(report=report, file=file)

        # Email → counselor
        counselor = report.counselor
        student_name = request.user.get_full_name() or request.user.username
        if counselor and counselor.email:
            safe_send_mail(
                subject=f'SafeSchool — Emploi du temps partagé — Dossier #{report.numero_dossier}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[counselor.email],
                message='',
                fail_silently=True,
                html_message=email_html(
                    title="Emploi du temps partagé par l'élève",
                    color='#0d9488',
                    body=f"""
                    <p>L'élève <strong>{student_name}</strong> a partagé son emploi du temps pour le dossier <strong>#{report.numero_dossier}</strong>.</p>
                    <p>Connectez-vous à la plateforme pour consulter le fichier et proposer un nouveau rendez-vous adapté à ses disponibilités.</p>
                    """
                )
            )

        return Response(
            ScheduleSerializer(schedule, context={'request': request}).data,
            status=201
        )

    def get(self, request, pk):
        if request.user.role not in ('directeur', 'conseiller'):
            return Response(status=403)
        try:
            report   = Report.objects.get(pk=pk)
            schedule = report.schedule
        except (Report.DoesNotExist, StudentSchedule.DoesNotExist):
            return Response(status=404)
        return Response(ScheduleSerializer(schedule, context={'request': request}).data)


# ── Annonces ─────────────────────────────────────────────────────────────────

class AnnonceListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = Annonce.objects.all()
        # Anonymous users and non-directors only see published announcements
        is_director = request.user.is_authenticated and request.user.role == 'directeur'
        if not is_director:
            qs = qs.filter(publie=True)
        return Response(AnnonceSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        if not request.user.is_authenticated or request.user.role != 'directeur':
            return Response(status=403)
        s = AnnonceSerializer(data=request.data, context={'request': request})
        if s.is_valid():
            s.save(auteur=request.user)
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class AnnonceDetailView(APIView):
    permission_classes = [IsDirecteur]

    def get_object(self, pk):
        try:
            return Annonce.objects.get(pk=pk)
        except Annonce.DoesNotExist:
            return None

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(status=404)
        s = AnnonceSerializer(obj, data=request.data, partial=True, context={'request': request})
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(status=404)
        obj.delete()
        return Response(status=204)


# ── Activités ────────────────────────────────────────────────────────────────

class ActiviteListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = Activite.objects.all()
        return Response(ActiviteSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        if not request.user.is_authenticated or request.user.role != 'directeur':
            return Response(status=403)
        s = ActiviteSerializer(data=request.data, context={'request': request})
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class ActiviteDetailView(APIView):
    permission_classes = [IsDirecteur]

    def get_object(self, pk):
        try:
            return Activite.objects.get(pk=pk)
        except Activite.DoesNotExist:
            return None

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(status=404)
        s = ActiviteSerializer(obj, data=request.data, partial=True, context={'request': request})
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(status=404)
        obj.delete()
        return Response(status=204)


# ── Contenu du site ──────────────────────────────────────────────────────────

class SiteContentView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        contents = SiteContent.objects.all()
        return Response(SiteContentSerializer(contents, many=True).data)

    def post(self, request):
        """Bulk upsert: accepts a list of {key, label, value, content_type}"""
        if request.user.role != 'directeur':
            return Response(status=403)
        items = request.data if isinstance(request.data, list) else [request.data]
        updated = []
        for item in items:
            key = item.get('key')
            if not key:
                continue
            obj, _ = SiteContent.objects.get_or_create(key=key)
            s = SiteContentSerializer(obj, data=item, partial=True)
            if s.is_valid():
                s.save()
                updated.append(s.data)
        return Response(updated)


# ── Photos ────────────────────────────────────────────────────────────────────

class PhotoListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsDirecteur()]

    def get(self, request):
        category = request.query_params.get('category')
        qs = Photo.objects.all()
        if category:
            qs = qs.filter(category=category)
        return Response(PhotoSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        s = PhotoSerializer(data=request.data, context={'request': request})
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class PhotoDetailView(APIView):
    permission_classes = [IsDirecteur]

    def patch(self, request, pk):
        try:
            photo = Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            return Response(status=404)
        s = PhotoSerializer(photo, data=request.data, partial=True, context={'request': request})
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, pk):
        try:
            photo = Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            return Response(status=404)
        photo.image.delete(save=False)  # supprime le fichier physique
        photo.delete()
        return Response(status=204)


# ── Import CSV élèves ─────────────────────────────────────────────────────────

class StudentImportView(APIView):
    """POST /api/students/import/ — importe un ou plusieurs fichiers Excel/CSV par niveau."""
    permission_classes = [IsDirecteur]
    parser_classes = [MultiPartParser, FormParser]

    VALID_NIVEAUX = {'1APIC', '2APIC', '3APIC'}
    VALID_NUMS    = set(str(i) for i in range(1, 11))

    @staticmethod
    def _normalize_classe(s):
        """'1APIC1' → '1APIC-1', '1APIC-1' → '1APIC-1'."""
        import re
        if not s:
            return ''
        s = s.strip().upper().replace(' ', '')
        if re.match(r'^\d+APIC-\d+$', s):
            return s
        m = re.match(r'^(\d+APIC)(\d+)$', s)
        return f"{m.group(1)}-{m.group(2)}" if m else s

    def _parse_raw_rows(self, file):
        """Retourne une liste de dicts depuis CSV ou Excel.
        Injecte '_sheet' (nom de feuille) et '_filename' (depuis le nom du fichier)
        pour résoudre automatiquement la classe quand la colonne 'classe' est absente.
        """
        import re
        name = file.name.lower()
        raw  = file.read()
        stem = re.sub(r'\.(xlsx?|csv)$', '', file.name, flags=re.IGNORECASE).strip()
        filename_class = self._normalize_classe(stem)

        if name.endswith('.xlsx') or name.endswith('.xls'):
            import openpyxl
            wb   = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
            rows_all = []
            for ws in wb.worksheets:
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    continue
                headers = [str(c).strip().lower() if c else '' for c in rows[0]]
                sheet_class = self._normalize_classe(ws.title.strip())
                for row in rows[1:]:
                    if all(v is None or str(v).strip() == '' for v in row):
                        continue
                    d = {headers[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(row)}
                    d['_sheet']    = sheet_class
                    d['_filename'] = filename_class
                    rows_all.append(d)
            return rows_all
        else:
            content = raw.decode('utf-8-sig')
            reader  = csv.DictReader(io.StringIO(content))
            return [
                {**{k.strip().lower(): (v or '').strip() for k, v in row.items()},
                 '_sheet': '', '_filename': filename_class}
                for row in reader
            ]

    def _build_classe(self, niveau, classe_raw):
        if not classe_raw:
            return None
        if '-' in classe_raw:
            return classe_raw.upper()
        if classe_raw.isdigit():
            return f"{niveau}-{classe_raw}"
        return classe_raw.upper()

    def _make_identifiant(self, prenom, nom, seen):
        import unicodedata, re
        def clean(s):
            s = unicodedata.normalize('NFD', s)
            s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
            return re.sub(r'[^a-zA-Z0-9]', '', s).lower()
        base = f"{clean(prenom)}.{clean(nom)}" if prenom else clean(nom)
        candidate = base
        suffix = 1
        while candidate in seen:
            candidate = f"{base}{suffix}"
            suffix += 1
        seen.add(candidate)
        return candidate

    def post(self, request):
        import re
        # Accepte un ou plusieurs fichiers (files[] ou file)
        files = request.FILES.getlist('files')
        if not files and 'file' in request.FILES:
            files = [request.FILES['file']]
        if not files:
            return Response({'error': 'Fichier(s) requis (CSV ou Excel).'}, status=400)

        replace_all    = request.data.get('replace_all', '0') == '1'
        replace_niveau = request.data.get('replace_niveau', '').strip().upper()

        if replace_all:
            User.objects.filter(role='etudiant').delete()
        elif replace_niveau in self.VALID_NIVEAUX:
            User.objects.filter(role='etudiant', classe__startswith=replace_niveau + '-').delete()

        parsed, errors, seen_ids, seen_usernames = [], [], set(), set()
        existing_usernames = set(User.objects.values_list('username', flat=True))

        for file in files:
            try:
                raw_rows = self._parse_raw_rows(file)
            except Exception as e:
                errors.append({'fichier': file.name, 'erreur': f'Impossible de lire le fichier : {e}'})
                continue

            for i, row in enumerate(raw_rows, start=2):
                nom    = (row.get('nom') or '').strip()
                prenom = (row.get('prenom') or row.get('prénom') or '').strip()

                if not nom and not prenom:
                    errors.append({'fichier': file.name, 'ligne': i, 'erreur': 'Nom et prénom manquants.'})
                    continue

                # Résolution de la classe : colonne (classe/class) > nom de fichier > nom de feuille
                classe_col = (row.get('classe') or row.get('class') or '').strip()
                if classe_col:
                    classe = self._normalize_classe(classe_col)
                    if not classe:
                        niveau_col = (row.get('niveau') or '').strip().upper()
                        classe = self._build_classe(niveau_col, classe_col) or ''
                else:
                    # Priorité au nom de fichier (ex: 1APIC-1) plutôt qu'au nom de feuille (FEUIL1)
                    classe = row.get('_filename') or row.get('_sheet') or ''

                # Extraire le niveau depuis la classe
                niveau = ''
                if classe:
                    m = re.match(r'^(\d+APIC)', classe.upper())
                    if m:
                        niveau = m.group(1)
                        if niveau not in self.VALID_NIVEAUX:
                            errors.append({'fichier': file.name, 'ligne': i, 'nom': f'{prenom} {nom}',
                                           'erreur': f'Niveau invalide : "{niveau}".'})
                            continue

                identifiant = (row.get('identifiant') or '').strip()
                if not identifiant:
                    identifiant = self._make_identifiant(prenom, nom, seen_ids)
                else:
                    if identifiant in seen_ids:
                        continue
                    seen_ids.add(identifiant)

                username = f"{identifiant}@safeschool.ma"
                if username in existing_usernames or username in seen_usernames:
                    User.objects.filter(username=username, role='etudiant').delete()
                seen_usernames.add(username)

                parsed.append({'nom': nom, 'prenom': prenom, 'niveau': niveau,
                               'classe': classe, 'identifiant': identifiant})

        to_create, created_meta = [], []
        for r in parsed:
            password = gen_password()
            username = f"{r['identifiant']}@safeschool.ma"
            to_create.append(User(
                username=username,
                password=make_password(password, hasher='md5'),
                first_name=r['prenom'],
                last_name=r['nom'],
                role='etudiant',
                identifiant=r['identifiant'],
                classe=r['classe'],
                is_active=True,
                must_change_password=True,
            ))
            created_meta.append({
                'first_name': r['prenom'], 'last_name': r['nom'],
                'niveau': r['niveau'], 'classe': r['classe'],
                'username': username, 'password': password,
            })

        if to_create:
            User.objects.bulk_create(to_create)

        return Response({
            'created': created_meta,
            'errors': errors,
            'total_created': len(created_meta),
            'total_errors': len(errors),
        })


# ── Reset password par le directeur ──────────────────────────────────────────

class StudentResetPasswordView(APIView):
    """POST /api/students/<pk>/reset-password/ — génère un nouveau mot de passe."""
    permission_classes = [IsDirecteur]

    def post(self, request, pk):
        try:
            student = User.objects.get(pk=pk, role='etudiant')
        except User.DoesNotExist:
            return Response(status=404)

        password = gen_password()
        student.password = make_password(password, hasher='md5')
        student.must_change_password = True
        student.save()

        return Response({'new_password': password, 'username': student.username})


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationListView(APIView):
    """GET /api/notifications/ — liste des notifications de l'utilisateur connecté."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(notifs, many=True).data)


class NotificationDetailView(APIView):
    """PATCH /api/notifications/<pk>/read/ — marquer comme lu."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(status=404)
        notif.is_read = True
        notif.save()
        return Response({'status': 'ok'})


class NotificationReadAllView(APIView):
    """POST /api/notifications/read-all/ — marquer toutes comme lues."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})


# ── Change password (premier login) ──────────────────────────────────────────

class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — forcer changement de mot de passe."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_password = request.data.get('new_password', '').strip()
        if len(new_password) < 6:
            return Response({'error': 'Le mot de passe doit contenir au moins 6 caractères.'}, status=400)
        request.user.set_password(new_password)
        request.user.must_change_password = False
        request.user.save()
        return Response({'status': 'ok'})
