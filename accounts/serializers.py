import re
from rest_framework import serializers
from .models import User

SEQUENTIAL = re.compile(r'(?:0123|1234|2345|3456|4567|5678|6789|abcd|bcde|cdef|defg|efgh|fghi|ghij)', re.I)
REPEATED   = re.compile(r'(.)\1{3,}')


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    confirm   = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password', 'confirm', 'telephone', 'classe']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9._\-]+$', value):
            raise serializers.ValidationError(
                "Format invalide. Utilisez uniquement des lettres, chiffres, points (.) ou tirets (-), sans espaces."
            )
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Ce nom d'utilisateur est déjà pris. Choisissez-en un autre (ex: said2, said.tallouk)."
            )
        return value

    def validate_email(self, value):
        if not value.lower().endswith('@gmail.com'):
            raise serializers.ValidationError(
                "Seules les adresses Gmail (@gmail.com) sont acceptées."
            )
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Cette adresse e-mail est déjà utilisée par un autre compte."
            )
        return value

    def validate_telephone(self, value):
        if value and User.objects.filter(telephone=value).exists():
            raise serializers.ValidationError(
                "Ce numéro de téléphone est déjà associé à un autre compte."
            )
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Minimum 8 caractères.')
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Ajoutez au moins une lettre minuscule (a-z).')
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Ajoutez au moins une lettre majuscule (A-Z).')
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('Ajoutez au moins un chiffre (0-9).')
        if not re.search(r'[!@#$%^&*\-_]', value):
            raise serializers.ValidationError('Ajoutez au moins un signe spécial (!@#$%^&*-_).')
        if SEQUENTIAL.search(value):
            raise serializers.ValidationError('Évitez les séquences successives (ex: 1234, abcd).')
        if REPEATED.search(value):
            raise serializers.ValidationError('Évitez les caractères répétés (ex: 1111, aaaa).')
        return value

    def validate(self, data):
        if data['password'] != data.pop('confirm'):
            raise serializers.ValidationError({'confirm': 'Les mots de passe ne correspondent pas.'})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username   = validated_data['username'],
            email      = validated_data['email'],
            password   = validated_data['password'],
            first_name = validated_data.get('first_name', ''),
            last_name  = validated_data.get('last_name', ''),
            telephone  = validated_data.get('telephone', ''),
            classe     = validated_data.get('classe', ''),
            role       = 'etudiant',
            is_active  = True,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name',
                  'email', 'role', 'telephone', 'classe', 'is_active', 'photo_url',
                  'date_joined', 'must_change_password']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url if obj.photo else None
