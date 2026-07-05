import random
import base64
import uuid
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, PasswordResetToken
from .serializers import RegisterSerializer, UserSerializer


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Nom d\'utilisateur ou mot de passe incorrect.'}, status=400)
        if not user.check_password(password):
            return Response({'error': 'Nom d\'utilisateur ou mot de passe incorrect.'}, status=400)
        if not user.is_active:
            return Response({'error': 'Votre compte est désactivé. Contactez le directeur.'}, status=403)
        return Response({**get_tokens(user), 'user': UserSerializer(user).data})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response({'message': 'Compte créé avec succès. Vous pouvez maintenant vous connecter.'}, status=201)
        return Response(s.errors, status=400)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name  = request.data.get('last_name',  user.last_name)
        user.email      = request.data.get('email',      user.email)
        user.telephone  = request.data.get('telephone',  user.telephone)
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
        user.save()
        return Response(UserSerializer(user, context={'request': request}).data)


class UploadPhotoView(APIView):
    """Endpoint dédié upload photo via base64 JSON — plus rapide que multipart."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data64 = request.data.get('photo_base64', '')
        if not data64:
            return Response({'error': 'Aucune image reçue.'}, status=400)
        try:
            # Format: "data:image/jpeg;base64,/9j/..."
            if ',' in data64:
                _, data64 = data64.split(',', 1)
            img_bytes = base64.b64decode(data64)
            filename  = f"profile_{request.user.id}_{uuid.uuid4().hex[:8]}.jpg"
            request.user.photo.save(filename, ContentFile(img_bytes), save=True)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response(UserSerializer(request.user, context={'request': request}).data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        role  = request.data.get('role', 'etudiant')
        if not email or '@' not in email:
            return Response({'error': 'Veuillez saisir une adresse e-mail valide.'}, status=400)
        roles = ['directeur', 'conseiller'] if role == 'staff' else ['etudiant']
        user  = User.objects.filter(email__iexact=email, role__in=roles).order_by('-id').first()
        if not user:
            return Response({'error': 'Aucun compte associé à cette adresse e-mail.'}, status=404)
        code    = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires = timezone.now() + timedelta(minutes=10)
        PasswordResetToken.objects.filter(user=user).delete()
        PasswordResetToken.objects.create(user=user, token=code, expires_at=expires)
        send_mail(
            subject='SafeSchool — Code de vérification',
            message=f'Votre code de vérification : {code} — valide 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
            html_message=f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:32px 16px;">
    <table width="480" cellpadding="0" cellspacing="0" style="background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
      <tr><td style="background:#1d4ed8;padding:24px 32px;">
        <p style="margin:0;font-size:1.3rem;font-weight:900;color:white;">&#128737; SafeSchool</p>
        <p style="margin:6px 0 0;font-size:1rem;color:rgba(255,255,255,0.85);font-weight:600;">R&#233;initialisation du mot de passe</p>
      </td></tr>
      <tr><td style="padding:32px;color:#334155;font-size:0.95rem;line-height:1.7;text-align:center;">
        <p style="margin:0 0 8px;">Bonjour <strong>{user.get_full_name() or user.username}</strong>,</p>
        <p style="margin:0 0 24px;color:#64748b;">Voici votre code de v&#233;rification :</p>
        <div style="font-size:2.8rem;font-weight:900;letter-spacing:14px;color:#1d4ed8;background:#eff6ff;padding:22px;border-radius:14px;">{code}</div>
        <p style="margin:20px 0 0;color:#92400e;font-size:0.85rem;">&#9200; Ce code est valable <strong>10 minutes</strong> uniquement.</p>
        <p style="margin:8px 0 0;color:#94a3b8;font-size:0.8rem;">Si vous n'avez pas demand&#233; cette r&#233;initialisation, ignorez cet e-mail.</p>
      </td></tr>
      <tr><td style="padding:16px 32px;background:#f8fafc;border-top:1px solid #e2e8f0;text-align:center;">
        <p style="margin:0;font-size:0.78rem;color:#94a3b8;">Cet e-mail a &#233;t&#233; envoy&#233; automatiquement par SafeSchool. Ne pas r&#233;pondre.</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""
        )
        masked = email[:2] + '***' + email[email.find('@'):]
        return Response({'message': 'Code de vérification envoyé.', 'masked_email': masked})


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        code  = request.data.get('code', '').strip()
        user  = User.objects.filter(email__iexact=email).order_by('-id').first()
        if not user:
            return Response({'error': 'Adresse e-mail introuvable.'}, status=404)
        token = PasswordResetToken.objects.filter(
            user=user, token=code, used=False, expires_at__gt=timezone.now()
        ).first()
        if not token:
            return Response({'error': 'Code incorrect ou expiré.'}, status=400)
        token.used = True
        token.save()
        temp = RefreshToken.for_user(user)
        return Response({'reset_token': str(temp.access_token)})


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current  = request.data.get('current_password', '').strip()
        password = request.data.get('password', '').strip()
        confirm  = request.data.get('confirm', '').strip()
        if current and not request.user.check_password(current):
            return Response({'error': 'Mot de passe actuel incorrect.'}, status=400)
        if len(password) < 6:
            return Response({'error': 'Le mot de passe doit contenir au moins 6 caractères.'}, status=400)
        if password != confirm:
            return Response({'error': 'Les mots de passe ne correspondent pas.'}, status=400)
        request.user.set_password(password)
        request.user.save()
        return Response({'message': 'Mot de passe modifié avec succès.'})
