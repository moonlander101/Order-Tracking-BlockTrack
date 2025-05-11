from django.urls import path
from .views import DocsCreate, DocsList, DocLinkGenerate

urlpatterns = [
    path("docs/<int:order_id>", DocsCreate.as_view()),
    path("docs/list", DocsList.as_view()),
    path("docs/links", DocLinkGenerate.as_view()),
]
