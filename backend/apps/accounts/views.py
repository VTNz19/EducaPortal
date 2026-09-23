import resend
from django.conf import settings
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.utils import registrar_log
from .models import PasswordResetToken, User
from .serializers import (
    CustomTokenObtainPairSerializer,
    EsqueciSenhaSerializer,
    MeSerializer,
    RedefinirSenhaSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            usuario = User.objects.filter(email=email).first()
            registrar_log(usuario, 'login_sucesso', detalhes=f'login: {email}', request=request)
        else:
            registrar_log(None, 'login_falha', detalhes=f'tentativa de login: {email}', request=request)

        return response


class MeView(RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EsqueciSenhaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EsqueciSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        usuario = User.objects.filter(email=email).first()
        if usuario:
            reset_token = PasswordResetToken.objects.create(usuario=usuario)
            link = f"{settings.FRONTEND_URL}/redefinir-senha?token={reset_token.token}"

            resend.api_key = settings.RESEND_API_KEY
            try:
                resend.Emails.send({
                    "from": "EducaPortal <onboarding@resend.dev>",
                    "to": [usuario.email],
                    "subject": "Redefinição de senha - EducaPortal",
                    "html": (
                        f"<p>Olá, {usuario.get_full_name() or usuario.username}.</p>"
                        f"<p>Recebemos um pedido para redefinir sua senha no EducaPortal.</p>"
                        f'<p><a href="{link}">Clique aqui para criar uma nova senha</a></p>'
                        f"<p>Este link expira em 1 hora. Se você não solicitou isso, ignore este e-mail.</p>"
                    ),
                })
            except Exception as erro:
                registrar_log(
                    usuario, 'esqueci_senha_falha_envio',
                    detalhes=f'e-mail: {email} | erro: {erro}', request=request,
                )
                return Response(
                    {'detail': 'Não foi possível enviar o e-mail agora. Tente novamente mais tarde.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            registrar_log(usuario, 'esqueci_senha_solicitado', detalhes=f'e-mail: {email}', request=request)


        return Response({'detail': 'Se o e-mail existir, enviamos um link de redefinição.'})



class RedefinirSenhaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RedefinirSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_valor = serializer.validated_data['token']
        nova_senha = serializer.validated_data['nova_senha']

        reset_token = PasswordResetToken.objects.filter(token=token_valor).first()

        if not reset_token or not reset_token.esta_valido():
            registrar_log(
                None, 'redefinir_senha_falha',
                detalhes=f'token inválido/expirado: {token_valor}', request=request,
            )
            return Response({'detail': 'Token inválido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        usuario = reset_token.usuario
        usuario.set_password(nova_senha)
        usuario.save()

        reset_token.usado = True
        reset_token.save()

        registrar_log(usuario, 'senha_redefinida', detalhes='senha redefinida via token', request=request)

        return Response({'detail': 'Senha redefinida com sucesso.'})
