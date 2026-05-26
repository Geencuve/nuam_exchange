"""
URL configuration for nuam_exchange project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from appNuam import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('appNuam.urls')),
    path("", views.dashboard_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("login/", views.login_view, name="login"),

    path("usuarios/", views.usuarios_lista_view, name="usuarios_lista"),
    path("", views.dashboard_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("login/", views.login_view, name="login"),

    path("usuarios/", views.usuarios_lista_view, name="usuarios_lista"),
    path("usuarios/nuevo/", views.usuario_form_view, name="usuario_form"),

    path("paises/", views.paises_lista_view, name="paises_lista"),
    path("paises/nuevo/", views.pais_form_view, name="pais_form"),

    path("normativas/", views.normativas_lista_view, name="normativas_lista"),
    path('normativas/nuevo/', views.normativa_form_view, name='normativa_form'),
    path('normativas/<int:normativa_id>/configurar/', views.normativa_configurar_view, name='normativa_configurar'),
  

    path("factores/", views.factores_lista_view, name="factores_lista"),
    path("factores/nuevo/", views.factores_form_view, name="factores_form"),

    path("reglas/", views.reglas_lista_view, name="reglas_lista"),
    path("reglas/nuevo/", views.regla_form_view, name="regla_form"),

    path("archivos-carga/", views.archivos_carga_lista_view, name="archivos_carga_lista"),
    path("archivos-carga/nuevo/", views.archivo_carga_form_view, name="archivo_carga_form"),

    path("calificaciones/", views.calificaciones_lista_view, name="calificaciones_lista"),
    path("calificaciones/nuevo/", views.calificacion_form_view, name="calificacion_form"),

    path("auditoria/", views.auditoria_lista_view, name="auditoria_lista"),
    path('auditoria/exportar/', views.auditoria_exportar_view, name='auditoria_exportar'),
    path('documentos/', views.documentos_lista_view, name='documentos_lista'),
    path('documentos/nuevo/', views.documento_pdf_form_view, name='documento_pdf_form'),
    path('documentos/<int:pk>/procesar/', views.documento_procesar_view, name='documento_procesar_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)