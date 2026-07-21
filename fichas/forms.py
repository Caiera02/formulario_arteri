from django import forms
from .models import FichaCadastral


class FichaCadastralForm(forms.ModelForm):
    """
    Formulário baseado no modelo FichaCadastral para validação dos dados
    de entrada de novos cadastros de locação.
    """

    class Meta:
        model = FichaCadastral
        fields = [
            "nome", "cpf", "rg", "nascimento", "estado_civil", "telefone",
            "celular", "email", "profissao", "empresa", "renda",
            "tempo_emprego", "cep", "cidade", "bairro", "rua", "numero",
            "tempo_residencia", "imovel_endereco", "imovel_proprietario",
            "imovel_aluguel", "imovel_condominio", "imovel_iptu",
            "imovel_residentes", "garantia_tipo", "ref1_nome",
            "ref1_telefone", "ref2_nome", "ref2_telefone", "observacoes",
            "lgpd_consent"
        ]

    def clean_lgpd_consent(self):
        """
        Garante que o consentimento da LGPD foi aceito.
        """
        consent = self.cleaned_data.get("lgpd_consent")
        if not consent:
            raise forms.ValidationError(
                "É obrigatório aceitar os termos da LGPD para continuar."
            )
        return consent

    def clean_cpf(self):
        """
        Valida o CPF de acordo com o algoritmo oficial da Receita Federal
        e o padroniza para o formato 000.000.000-00.
        """
        cpf_valor = self.cleaned_data.get("cpf")
        if not cpf_valor:
            raise forms.ValidationError("CPF é obrigatório.")

        import re
        # Remove caracteres não numéricos
        cpf_limpo = re.sub(r"\D", "", cpf_valor)

        if len(cpf_limpo) != 11:
            raise forms.ValidationError("O CPF deve conter exatamente 11 dígitos.")

        # Evita sequências de números iguais conhecidas (ex: 111.111.111-11)
        if cpf_limpo in [str(i) * 11 for i in range(10)]:
            raise forms.ValidationError("CPF inválido.")

        # Validação do primeiro dígito verificador
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf_limpo[9]):
            raise forms.ValidationError("CPF inválido.")

        # Validação do segundo dígito verificador
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf_limpo[10]):
            raise forms.ValidationError("CPF inválido.")

        # Formata para salvar padronizado
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf_formatado

