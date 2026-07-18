from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import FichaCadastralForm
from .models import FichaCadastral, LogAuditoria


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin para garantir que apenas usuários autenticados e que sejam
    membros da equipe (staff) ou superusuários tenham acesso à view.
    """
    login_url = "fichas:login"

    def test_func(self):
        return (
            self.request.user.is_authenticated 
            and (self.request.user.is_staff or self.request.user.is_superuser)
        )



class FichaCadastralView(View):
    """
    View baseada em classe para exibição e processamento do formulário
    de cadastro de fichas cadastrais da Arteri Imóveis.
    """

    def get(self, request, *args, **kwargs):
        """
        Exibe o formulário de locação cadastral limpo.
        """
        form = FichaCadastralForm()
        return render(request, "fichas/formulario_locacao.html", {"form": form})

    def post(self, request, *args, **kwargs):
        """
        Processa o envio dos dados do formulário de locação.
        Retorna JSON com status de sucesso ou erro de validação.
        """
        form = FichaCadastralForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            
            # Registra auditoria de novo cadastro
            LogAuditoria.objects.create(
                acao=f"Novo cadastro enviado pelo candidato: {ficha.nome} (CPF: {ficha.cpf})"
            )
            
            return JsonResponse({"ok": True, "id": ficha.id})
        else:
            # Formata os erros de validação em português legível
            erros = []
            for campo, lista_erros in form.errors.items():
                # Tenta recuperar o rótulo do campo, senão usa o nome do campo
                campo_obj = form.fields.get(campo)
                label = campo_obj.label if campo_obj and campo_obj.label else campo
                erros.append(f"{label}: {lista_erros[0]}")

            mensagem_erro = "Erros de validação: " + "; ".join(erros)
            return JsonResponse({"ok": False, "erro": mensagem_erro}, status=400)


class FichaCadastralLoginView(LoginView):
    """
    View baseada em classe para autenticação de corretores
    no painel de controle da Arteri Imóveis.
    """

    template_name = "fichas/login.html"
    redirect_authenticated_user = True


class FichaCadastralLogoutView(View):
    """
    View baseada em classe para encerrar a sessão de corretores.
    """

    def get(self, request, *args, **kwargs):
        """Suporta logout via GET (comum em links)"""
        logout(request)
        return redirect("fichas:login")

    def post(self, request, *args, **kwargs):
        """Suporta logout via POST"""
        logout(request)
        return redirect("fichas:login")




class FichaCadastralListView(StaffRequiredMixin, ListView):
    """
    View baseada em classe para listar e gerenciar todos os formulários
    enviados. Requer autenticação do usuário.
    """

    model = FichaCadastral
    template_name = "fichas/dashboard.html"
    context_object_name = "fichas"
    login_url = "fichas:login"  # Redireciona para a nova tela de login local

    def get_queryset(self):
        """
        Permite buscar fichas pelo nome ou CPF se informado na query.
        """
        queryset = super().get_queryset()
        busca = self.request.GET.get("busca")
        if busca:
            queryset = queryset.filter(
                nome__icontains=busca
            ) | queryset.filter(
                cpf__contains=busca
            )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adiciona estatísticas rápidas ao contexto do painel de gerenciamento.
        """
        context = super().get_context_data(**kwargs)
        all_fichas = FichaCadastral.objects.all()
        context["total_fichas"] = all_fichas.count()

        # Contagem por status
        context["total_novas"] = all_fichas.filter(status="novo").count()
        context["total_analise"] = all_fichas.filter(status="analise").count()
        context["total_consultadas"] = all_fichas.filter(
            status="consultado"
        ).count()
        context["total_pagas"] = all_fichas.filter(status="pago").count()

        # Contagem por tipo de garantia
        garantias = {}
        for f in all_fichas:
            garantias[f.garantia_tipo] = garantias.get(f.garantia_tipo, 0) + 1
        context["garantias_stats"] = garantias
        return context


class FichaCadastralDetailJSONView(StaffRequiredMixin, DetailView):
    """
    View para retornar os dados completos de uma ficha cadastral em JSON.
    Utilizada para carregar detalhes interativamente via AJAX no painel.
    """

    model = FichaCadastral
    login_url = "fichas:login"  # Redireciona para a nova tela de login local

    def get(self, request, *args, **kwargs):
        ficha = self.get_object()
        data = {
            "id": ficha.id,
            "nome": ficha.nome,
            "cpf": ficha.cpf,
            "rg": ficha.rg,
            "nascimento": (
                ficha.nascimento.strftime("%d/%m/%Y")
                if ficha.nascimento
                else ""
            ),
            "estado_civil": ficha.estado_civil,
            "telefone": ficha.telefone,
            "celular": ficha.celular,
            "email": ficha.email,
            "profissao": ficha.profissao,
            "empresa": ficha.empresa,
            "renda": f"R$ {ficha.renda:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            "tempo_emprego": ficha.tempo_emprego or "Não informado",
            "cep": ficha.cep,
            "cidade": ficha.cidade,
            "bairro": ficha.bairro,
            "rua": ficha.rua,
            "numero": ficha.numero,
            "tempo_residencia": ficha.tempo_residencia or "Não informado",
            "imovel_endereco": ficha.imovel_endereco or "",
            "imovel_proprietario": ficha.imovel_proprietario or "",
            "imovel_aluguel": (
                f"R$ {ficha.imovel_aluguel:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if ficha.imovel_aluguel
                else ""
            ),
            "imovel_condominio": (
                f"R$ {ficha.imovel_condominio:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if ficha.imovel_condominio
                else "N/A"
            ),
            "imovel_iptu": (
                f"R$ {ficha.imovel_iptu:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if ficha.imovel_iptu
                else "N/A"
            ),
            "imovel_residentes": ficha.imovel_residentes or "",
            "garantia_tipo": ficha.garantia_tipo or "",
            "ref1_nome": ficha.ref1_nome or "Não informado",
            "ref1_telefone": ficha.ref1_telefone or "Não informado",
            "ref2_nome": ficha.ref2_nome or "Não informado",
            "ref2_telefone": ficha.ref2_telefone or "Não informado",
            "observacoes": ficha.observacoes or "Sem observações adicionais.",
            "criado_em": (
                ficha.criado_em.strftime("%d/%m/%Y %H:%M:%S")
                if ficha.criado_em
                else ""
            ),
            # Status e Auditoria
            "status": ficha.status,
            "status_display": ficha.get_status_display(),
            "modificado_por": (
                ficha.modificado_por.username
                if ficha.modificado_por
                else "Nenhum"
            ),
            "modificado_em": (
                ficha.modificado_em.strftime("%d/%m/%Y %H:%M:%S")
                if ficha.modificado_por
                else "N/A"
            ),
        }
        return JsonResponse(data)


class FichaCadastralAtualizarStatusView(StaffRequiredMixin, View):
    """
    View baseada em classe para atualizar o status de uma FichaCadastral
    e registrar qual usuário autenticado realizou a alteração.
    """

    login_url = "fichas:login"  # Redireciona para a nova tela de login local

    def post(self, request, pk, *args, **kwargs):
        try:
            ficha = FichaCadastral.objects.get(pk=pk)
            novo_status = request.POST.get("status")

            # Valida se o status enviado é permitido
            valid_statuses = [c[0] for c in FichaCadastral.STATUS_CHOICES]
            if novo_status not in valid_statuses:
                return JsonResponse(
                    {"ok": False, "erro": "Status inválido."}, status=400
                )

            status_antigo = ficha.get_status_display()
            ficha.status = novo_status
            ficha.modificado_por = request.user
            ficha.save()

            # Registra log de auditoria
            LogAuditoria.objects.create(
                usuario=request.user,
                acao=f"Alterou o status da ficha de {ficha.nome}",
                detalhes=f"De: {status_antigo} | Para: {ficha.get_status_display()}"
            )

            return JsonResponse({
                "ok": True,
                "status_display": ficha.get_status_display(),
                "modificado_por": ficha.modificado_por.username,
                "modificado_em": ficha.modificado_em.strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),
            })
        except FichaCadastral.DoesNotExist:
            return JsonResponse(
                {"ok": False, "erro": "Ficha não encontrada."}, status=404
            )
        except Exception as e:
            return JsonResponse({"ok": False, "erro": str(e)}, status=500)


class FichaCadastralUpdateView(StaffRequiredMixin, View):
    """
    View baseada em classe para editar e atualizar as informações
    completas de uma FichaCadastral existente. Registrar qual
    corretor realizou as edições.
    """

    login_url = "fichas:login"

    def post(self, request, pk, *args, **kwargs):
        try:
            ficha = FichaCadastral.objects.get(pk=pk)
            form = FichaCadastralForm(request.POST, instance=ficha)
            
            if form.is_valid():
                # Detecta quais campos sofreram alteração
                changed_fields = form.changed_data
                
                # Salva os dados
                ficha = form.save(commit=False)
                ficha.modificado_por = request.user
                ficha.save()
                
                # Registra log de auditoria master
                if changed_fields:
                    nomes_campos = []
                    for f in changed_fields:
                        try:
                            nomes_campos.append(ficha._meta.get_field(f).verbose_name)
                        except:
                            nomes_campos.append(f)
                            
                    campos_alterados = ", ".join(nomes_campos)
                    detalhes = f"Campos editados: {campos_alterados}"
                else:
                    detalhes = "Formulário salvo sem alterações nos campos."
                
                LogAuditoria.objects.create(
                    usuario=request.user,
                    acao=f"Editou dados cadastrais da ficha de {ficha.nome}",
                    detalhes=detalhes
                )
                
                return JsonResponse({"ok": True, "msg": "Informações salvas com sucesso!"})
            else:
                erros = []
                for campo, lista_erros in form.errors.items():
                    campo_obj = form.fields.get(campo)
                    label = campo_obj.label if campo_obj and campo_obj.label else campo
                    erros.append(f"{label}: {lista_erros[0]}")
                
                mensagem_erro = "Erros de validação: " + "; ".join(erros)
                return JsonResponse({"ok": False, "erro": mensagem_erro}, status=400)
                
        except FichaCadastral.DoesNotExist:
            return JsonResponse({"ok": False, "erro": "Ficha não encontrada."}, status=404)
        except Exception as e:
            return JsonResponse({"ok": False, "erro": str(e)}, status=500)


class FichaCadastralAuditoriaListView(StaffRequiredMixin, ListView):
    """
    View baseada em classe para listar todos os logs de auditoria do sistema.
    Permite controle master e auditoria transparente (Acesso Master).
    """

    model = LogAuditoria
    template_name = "fichas/auditoria.html"
    context_object_name = "logs"
    login_url = "fichas:login"
