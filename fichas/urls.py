from django.urls import path
from .views import (
    FichaCadastralView,
    FichaCadastralListView,
    FichaCadastralDetailJSONView,
    FichaCadastralAtualizarStatusView,
    FichaCadastralLoginView,
    FichaCadastralLogoutView,
    FichaCadastralUpdateView,
    FichaCadastralAuditoriaListView
)

app_name = "fichas"

urlpatterns = [
    path("", FichaCadastralView.as_view(), name="formulario"),
    path("login/", FichaCadastralLoginView.as_view(), name="login"),
    path("logout/", FichaCadastralLogoutView.as_view(), name="logout"),
    path("gerenciar/", FichaCadastralListView.as_view(), name="dashboard"),
    path("gerenciar/auditoria/", FichaCadastralAuditoriaListView.as_view(), name="auditoria"),
    path(
        "gerenciar/detalhes/<int:pk>/",
        FichaCadastralDetailJSONView.as_view(),
        name="detalhes_json"
    ),
    path(
        "gerenciar/status/<int:pk>/",
        FichaCadastralAtualizarStatusView.as_view(),
        name="atualizar_status"
    ),
    path(
        "gerenciar/editar/<int:pk>/",
        FichaCadastralUpdateView.as_view(),
        name="editar_ficha"
    ),
]
