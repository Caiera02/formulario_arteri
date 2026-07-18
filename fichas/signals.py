import logging
import threading
import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FichaCadastral

logger = logging.getLogger(__name__)


def enviar_whatsapp_assincrono(url, headers, payload):
    """
    Executa a requisição HTTP POST para a API do WhatsApp em uma thread
    separada para evitar que o tempo de resposta da API atrase o fluxo
    do usuário final no cadastro do site.
    """
    def thread_envio():
        try:
            resposta = requests.post(url, headers=headers, json=payload, timeout=10)
            resposta.raise_for_status()
            logger.info(
                f"Mensagem de WhatsApp enviada com sucesso. Retorno: {resposta.text}"
            )
        except Exception as erro:
            logger.error(
                f"Falha ao tentar enviar mensagem de WhatsApp: {erro}"
            )

    thread = threading.Thread(target=thread_envio, daemon=True)
    thread.start()


@receiver(post_save, sender=FichaCadastral)
def enviar_notificacao_novo_cadastro(sender, instance, created, **kwargs):
    """
    Signal do Django que escuta a criação de instâncias de FichaCadastral.
    Dispara uma requisição para a API de WhatsApp com os dados principais.
    """
    if not created:
        return

    # Carrega as configurações definidas no settings do projeto
    base_url = getattr(
        settings, "WHATSAPP_API_BASE_URL", "https://api.exemplo.com"
    ).rstrip("/")
    api_url = f"{base_url}/api/v1/messages/send/text"
    secret_token = getattr(
        settings, "WHATSAPP_SECRET_TOKEN", "YOUR_SECRET_TOKEN"
    )
    session_id = getattr(
        settings, "WHATSAPP_SESSION_ID", "YOUR_SESSION_ID"
    )
    destinatario = getattr(
        settings, "WHATSAPP_RECIPIENT", "5511999999999@s.whatsapp.net"
    )

    # Formata o destinatário para garantir o sufixo necessário do WhatsApp
    if destinatario and not destinatario.endswith("@s.whatsapp.net"):
        destinatario = f"{destinatario}@s.whatsapp.net"

    # Constrói a URL do painel administrativo
    site_base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
    admin_url = f"{site_base_url}/gerenciar/"

    # Monta a mensagem de texto com a frase solicitada
    texto_mensagem = (
        f"Essa pessoa acabou de se cadastrar, clica para olhar:\n"
        f"{admin_url}"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": secret_token
    }

    payload = {
        "sessionId": session_id,
        "to": destinatario,
        "text": texto_mensagem,
        "contextInfo": {
            "stanzaId": "BAE5C3F2E3D4",
            "participant": destinatario,
            "remoteJid": destinatario,
            "mentionedJid": [destinatario],
            "quotedMessage": {
                "conversation": "Novo cadastro Arteri Imóveis"
            }
        },
        "mentionAll": True,
        "linkPreview": True,
        "linkPreviewUrl": "",
        "linkPreviewSmall": True,
        "async": True
    }

    enviar_whatsapp_assincrono(api_url, headers, payload)
