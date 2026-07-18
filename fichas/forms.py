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
