from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import FichaCadastral
from .forms import FichaCadastralForm


class FichaCadastralTestCase(TestCase):
    """
    Testes de unidade para o modelo, formulários, views e signals de fichas.
    """

    def setUp(self):
        self.dados_validos = {
            "nome": "João da Silva",
            "cpf": "123.456.789-00",
            "rg": "12.345.678-9",
            "nascimento": "1990-05-15",
            "estado_civil": "Solteiro(a)",
            "telefone": "(11) 2222-3333",
            "celular": "(11) 99999-8888",
            "email": "joao@exemplo.com",
            "profissao": "Engenheiro",
            "empresa": "Arteri Devs",
            "renda": 5500.00,
            "tempo_emprego": "3 anos",
            "cep": "01001-000",
            "cidade": "São Paulo",
            "bairro": "Sé",
            "rua": "Praça da Sé",
            "numero": "100",
            "tempo_residencia": "2 anos",
            "imovel_endereco": "Rua Augusta, 500",
            "imovel_proprietario": "Maria de Souza",
            "imovel_aluguel": 2500.00,
            "imovel_condominio": 400.00,
            "imovel_iptu": 150.00,
            "imovel_residentes": 2,
            "garantia_tipo": "Caução",
            "ref1_nome": "Pedro Santos",
            "ref1_telefone": "(11) 98888-7777",
            "ref2_nome": "Ana Oliveira",
            "ref2_telefone": "(11) 97777-6666",
            "observacoes": "Pretendo alugar rápido.",
            "lgpd_consent": True,
        }

    def test_criacao_ficha_cadastral(self):
        """
        Garante que o model FichaCadastral salva os dados corretamente.
        """
        ficha = FichaCadastral.objects.create(**self.dados_validos)
        self.assertEqual(ficha.nome, "João da Silva")
        self.assertEqual(ficha.cpf, "123.456.789-00")
        self.assertTrue(ficha.lgpd_consent)
        self.assertIsNotNone(ficha.criado_em)

    def test_validacao_formulario_sem_lgpd(self):
        """
        Garante que o formulário rejeita submissões sem consentimento da LGPD.
        """
        dados_sem_lgpd = self.dados_validos.copy()
        dados_sem_lgpd["lgpd_consent"] = False
        form = FichaCadastralForm(data=dados_sem_lgpd)
        self.assertFalse(form.is_valid())
        self.assertIn("lgpd_consent", form.errors)

    def test_view_formulario_get(self):
        """
        Garante que a view FichaCadastralView retorna a página com status 200.
        """
        resposta = self.client.get(reverse("fichas:formulario"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "fichas/formulario_locacao.html")

    @patch("fichas.signals.requests.post")
    def test_view_formulario_post_valido(self, mock_post):
        """
        Garante que o POST válido retorna resposta JSON de sucesso
        e que o signal dispara a notificação via WhatsApp.
        """
        resposta = self.client.post(
            reverse("fichas:formulario"),
            data=self.dados_validos,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resposta.status_code, 200)
        dados_json = resposta.json()
        self.assertTrue(dados_json["ok"])
        self.assertIn("id", dados_json)

        # Verifica se o model foi criado no banco
        self.assertEqual(FichaCadastral.objects.count(), 1)

        # Verifica se o signal tentou disparar a requisição HTTP do WhatsApp
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        from django.conf import settings
        recipient = getattr(settings, 'WHATSAPP_RECIPIENT', '5511999999999')
        if not recipient.endswith('@s.whatsapp.net'):
            recipient = f"{recipient}@s.whatsapp.net"
        self.assertEqual(kwargs["json"]["to"], recipient)
        self.assertIn("Essa pessoa acabou de se cadastrar", kwargs["json"]["text"])

    def test_view_formulario_post_invalido(self):
        """
        Garante que o POST inválido retorna resposta JSON de erro.
        """
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos["nome"] = ""  # Nome em branco é inválido
        resposta = self.client.post(
            reverse("fichas:formulario"),
            data=dados_invalidos,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resposta.status_code, 400)
        dados_json = resposta.json()
        self.assertFalse(dados_json["ok"])
        self.assertIn("erro", dados_json)

    def test_view_dashboard_deslogado(self):
        """
        Garante que usuários não autenticados são redirecionados para a tela
        de login ao tentar acessar o painel de gerenciamento.
        """
        resposta = self.client.get(reverse("fichas:dashboard"))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login/", resposta["Location"])

    def test_view_dashboard_logado(self):
        """
        Garante que usuários autenticados conseguem acessar o painel
        com sucesso.
        """
        usuario = User.objects.create_user(
            username="corretor", password="senha_secreta", is_staff=True
        )
        self.client.login(username="corretor", password="senha_secreta")

        resposta = self.client.get(reverse("fichas:dashboard"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "fichas/dashboard.html")

    def test_view_dashboard_usuario_comum_bloqueado(self):
        """
        Garante que um usuário autenticado comum (que não é staff) seja
        bloqueado (HTTP 403) ao tentar acessar o painel de gerenciamento.
        """
        usuario = User.objects.create_user(
            username="candidato", password="senha_secreta", is_staff=False
        )
        self.client.login(username="candidato", password="senha_secreta")

        resposta = self.client.get(reverse("fichas:dashboard"))
        self.assertEqual(resposta.status_code, 403)


    def test_view_detalhes_json_logado(self):
        """
        Garante que o endpoint JSON retorna os dados de detalhamento
        corretos para usuários autenticados.
        """
        ficha = FichaCadastral.objects.create(**self.dados_validos)
        usuario = User.objects.create_user(
            username="corretor", password="senha_secreta", is_staff=True
        )
        self.client.login(username="corretor", password="senha_secreta")

        resposta = self.client.get(
            reverse("fichas:detalhes_json", kwargs={"pk": ficha.pk})
        )
        self.assertEqual(resposta.status_code, 200)
        dados_json = resposta.json()
        self.assertEqual(dados_json["nome"], "João da Silva")
        self.assertEqual(dados_json["cpf"], "123.456.789-00")

    def test_status_padrao_novo(self):
        """
        Garante que toda nova ficha é criada com o status padrão 'novo'.
        """
        ficha = FichaCadastral.objects.create(**self.dados_validos)
        self.assertEqual(ficha.status, "novo")

    def test_atualizar_status_autenticado(self):
        """
        Garante que um corretor logado consegue atualizar o status de uma ficha
        e que o registro de quem modificou é salvo.
        """
        ficha = FichaCadastral.objects.create(**self.dados_validos)
        usuario = User.objects.create_user(
            username="corretor_auditor", password="senha_secreta", is_staff=True
        )
        self.client.login(username="corretor_auditor", password="senha_secreta")

        resposta = self.client.post(
            reverse("fichas:atualizar_status", kwargs={"pk": ficha.pk}),
            data={"status": "analise"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resposta.status_code, 200)
        dados_json = resposta.json()
        self.assertTrue(dados_json["ok"])
        self.assertEqual(dados_json["status_display"], "Em Análise")
        self.assertEqual(dados_json["modificado_por"], "corretor_auditor")

        # Verifica persistência no banco de dados
        ficha.refresh_from_db()
        self.assertEqual(ficha.status, "analise")
        self.assertEqual(ficha.modificado_por, usuario)
        self.assertIsNotNone(ficha.modificado_em)

    def test_atualizar_status_deslogado(self):
        """
        Garante que requisições não autenticadas para atualizar status
        sejam bloqueadas e redirecionadas para a tela de login.
        """
        ficha = FichaCadastral.objects.create(**self.dados_validos)
        resposta = self.client.post(
            reverse("fichas:atualizar_status", kwargs={"pk": ficha.pk}),
            data={"status": "pago"}
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login/", resposta["Location"])

    def test_secao_3_opcional(self):
        """
        Garante que os campos de Imóvel Pretendido e Garantia (Seção 3)
        são de fato opcionais e a validação do formulário passa sem eles.
        """
        dados_sem_secao_3 = self.dados_validos.copy()
        # Remove campos da seção 3
        dados_sem_secao_3["imovel_endereco"] = ""
        dados_sem_secao_3["imovel_proprietario"] = ""
        dados_sem_secao_3["imovel_aluguel"] = ""
        dados_sem_secao_3["imovel_residentes"] = ""
        dados_sem_secao_3["garantia_tipo"] = ""

        form = FichaCadastralForm(data=dados_sem_secao_3)
        self.assertTrue(form.is_valid())

    def test_editar_ficha_autenticado(self):
        """
        Garante que um corretor logado consegue editar dados cadastrais de uma ficha,
        registrando as alterações no LogAuditoria e o usuário responsável.
        """
        ficha = FichaCadastral.objects.create(**self.dados_validos)
        usuario = User.objects.create_user(
            username="corretor_editor", password="senha_secreta", is_staff=True
        )
        self.client.login(username="corretor_editor", password="senha_secreta")

        dados_novos = self.dados_validos.copy()
        dados_novos["nome"] = "João da Silva Alterado"
        dados_novos["renda"] = 8000.00

        resposta = self.client.post(
            reverse("fichas:editar_ficha", kwargs={"pk": ficha.pk}),
            data=dados_novos,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resposta.status_code, 200)
        dados_json = resposta.json()
        self.assertTrue(dados_json["ok"])

        # Verifica persistência no banco
        ficha.refresh_from_db()
        self.assertEqual(ficha.nome, "João da Silva Alterado")
        self.assertEqual(ficha.renda, 8000.00)
        self.assertEqual(ficha.modificado_por, usuario)

        # Verifica se o log de auditoria foi criado
        from .models import LogAuditoria
        self.assertTrue(LogAuditoria.objects.filter(usuario=usuario).exists())

    def test_auditoria_logs_restrito(self):
        """
        Garante que corretores autenticados conseguem acessar a view
        de logs de auditoria (Acesso Master).
        """
        usuario = User.objects.create_user(
            username="corretor_master", password="senha_secreta", is_staff=True
        )
        self.client.login(username="corretor_master", password="senha_secreta")

        resposta = self.client.get(reverse("fichas:auditoria"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "fichas/auditoria.html")

    def test_logout_get(self):
        """
        Garante que a view de logout aceita requisições GET e redireciona
        corretamente para a tela de login.
        """
        resposta = self.client.get(reverse("fichas:logout"))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login/", resposta["Location"])

    def test_logout_post(self):
        """
        Garante que a view de logout aceita requisições POST e redireciona
        corretamente para a tela de login.
        """
        resposta = self.client.post(reverse("fichas:logout"))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login/", resposta["Location"])



