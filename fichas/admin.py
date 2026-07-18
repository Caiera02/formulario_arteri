from django.contrib import admin
from .models import FichaCadastral, LogAuditoria


@admin.register(FichaCadastral)
class FichaCadastralAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "status", "imovel_aluguel", "criado_em")
    list_filter = ("status", "garantia_tipo", "criado_em")
    search_fields = ("nome", "cpf", "email")
    readonly_fields = ("criado_em", "modificado_em")


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "acao", "criado_em")
    list_filter = ("usuario", "criado_em")
    search_fields = ("acao", "detalhes")
    readonly_fields = ("criado_em",)
