from django.contrib.auth.models import User
from django.db import models


class FichaCadastral(models.Model):
    """
    Modelo para armazenar as fichas cadastrais enviadas pelos pretendentes
    de locação da Arteri Imóveis.
    """

    # Seção 1: Dados Pessoais
    nome = models.CharField(
        verbose_name="Nome Completo",
        max_length=120
    )
    cpf = models.CharField(
        verbose_name="CPF",
        max_length=20
    )
    rg = models.CharField(
        verbose_name="RG",
        max_length=20
    )
    nascimento = models.DateField(
        verbose_name="Data de Nascimento"
    )
    estado_civil = models.CharField(
        verbose_name="Estado Civil",
        max_length=30
    )
    telefone = models.CharField(
        verbose_name="Telefone Residencial",
        max_length=20
    )
    celular = models.CharField(
        verbose_name="Celular / WhatsApp",
        max_length=20
    )
    email = models.EmailField(
        verbose_name="E-mail"
    )

    # Seção 2: Dados Profissionais e Residenciais
    profissao = models.CharField(
        verbose_name="Profissão",
        max_length=80
    )
    empresa = models.CharField(
        verbose_name="Empresa",
        max_length=120
    )
    renda = models.DecimalField(
        verbose_name="Renda Mensal R$",
        max_digits=10,
        decimal_places=2
    )
    tempo_emprego = models.CharField(
        verbose_name="Tempo de Emprego",
        max_length=40,
        blank=True
    )
    cep = models.CharField(
        verbose_name="CEP",
        max_length=10
    )
    cidade = models.CharField(
        verbose_name="Cidade",
        max_length=100
    )
    bairro = models.CharField(
        verbose_name="Bairro",
        max_length=100
    )
    rua = models.CharField(
        verbose_name="Rua / Endereço",
        max_length=150
    )
    numero = models.CharField(
        verbose_name="Número",
        max_length=20
    )
    tempo_residencia = models.CharField(
        verbose_name="Tempo de Residência",
        max_length=40,
        blank=True
    )

    # Seção 3: Imóvel Pretendido e Garantias
    imovel_endereco = models.CharField(
        verbose_name="Endereço do Imóvel Pretendido",
        max_length=200,
        blank=True
    )
    imovel_proprietario = models.CharField(
        verbose_name="Proprietário do Imóvel",
        max_length=120,
        blank=True
    )
    imovel_aluguel = models.DecimalField(
        verbose_name="Valor do Aluguel R$",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    imovel_condominio = models.DecimalField(
        verbose_name="Valor do Condomínio R$",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    imovel_iptu = models.DecimalField(
        verbose_name="Valor do IPTU R$",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    imovel_residentes = models.PositiveIntegerField(
        verbose_name="Número de Residentes",
        null=True,
        blank=True
    )
    garantia_tipo = models.CharField(
        verbose_name="Tipo de Garantia",
        max_length=40,
        blank=True
    )

    # Seção 4: Referências Pessoais e LGPD
    ref1_nome = models.CharField(
        verbose_name="Referência 1 - Nome",
        max_length=120,
        blank=True
    )
    ref1_telefone = models.CharField(
        verbose_name="Referência 1 - Telefone",
        max_length=20,
        blank=True
    )
    ref2_nome = models.CharField(
        verbose_name="Referência 2 - Nome",
        max_length=120,
        blank=True
    )
    ref2_telefone = models.CharField(
        verbose_name="Referência 2 - Telefone",
        max_length=20,
        blank=True
    )
    observacoes = models.TextField(
        verbose_name="Observações",
        blank=True
    )
    lgpd_consent = models.BooleanField(
        verbose_name="Consentimento LGPD",
        default=False
    )

    # Auditoria
    criado_em = models.DateTimeField(
        verbose_name="Criado em",
        auto_now_add=True
    )

    # Status e Auditoria de Acompanhamento
    STATUS_CHOICES = [
        ("novo", "Cadastro Novo"),
        ("analise", "Em Análise"),
        ("consultado", "Consultado"),
        ("pago", "Pago"),
    ]
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="novo"
    )
    modificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modificado por",
        related_name="fichas_modificadas"
    )
    modificado_em = models.DateTimeField(
        verbose_name="Modificado em",
        auto_now=True
    )

    class Meta:
        verbose_name = "Ficha Cadastral"
        verbose_name_plural = "Fichas Cadastrais"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} - {self.cpf}"


class LogAuditoria(models.Model):
    """
    Modelo para registrar logs de auditoria de ações realizadas no sistema.
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário"
    )
    acao = models.CharField(
        max_length=250,
        verbose_name="Ação"
    )
    detalhes = models.TextField(
        verbose_name="Detalhes",
        blank=True,
        null=True
    )
    criado_em = models.DateTimeField(
        verbose_name="Data/Hora",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ["-criado_em"]

    def __str__(self):
        usr = self.usuario.username if self.usuario else "Sistema/Candidato"
        return f"{usr} - {self.acao} em {self.criado_em.strftime('%d/%m/%Y %H:%M:%S')}"

