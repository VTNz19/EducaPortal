from rest_framework import serializers

from apps.accounts.mascaras import mascarar_emails_no_texto

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    detalhes = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'acao', 'detalhes', 'endereco_ip', 'criado_em']

    def get_detalhes(self, obj):
        """Os e-mails citados nos detalhes aparecem mascarados, exceto na exportação ao titular (RN88)."""
        if self.context.get('emails_completos'):
            return obj.detalhes
        return mascarar_emails_no_texto(obj.detalhes)
