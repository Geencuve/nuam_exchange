from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentoDigitalViewSet
from .views import (
    RolViewSet,
    UsuarioViewSet,
    UsuarioRolViewSet,
    SesionAccesoViewSet,
    PaisViewSet,
    NormativaTributariaViewSet,
    InstrumentoFinancieroViewSet,
    FactorTributarioViewSet,
    ReglaConversionViewSet,
    ArchivoCargaViewSet,
    DetalleCargaViewSet,
    ProcesoConversionViewSet,
    CalificacionTributariaViewSet,
    AuditoriaCambioViewSet,
    BitacoraSistemaViewSet,
)
from . import views

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='roles')
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'usuario-roles', UsuarioRolViewSet, basename='usuario-roles')
router.register(r'sesiones-acceso', SesionAccesoViewSet, basename='sesiones-acceso')
router.register(r'paises', PaisViewSet, basename='paises')
router.register(r'normativas-tributarias', NormativaTributariaViewSet, basename='normativas-tributarias')
router.register(r'instrumentos-financieros', InstrumentoFinancieroViewSet, basename='instrumentos-financieros')
router.register(r'factores-tributarios', FactorTributarioViewSet, basename='factores-tributarios')
router.register(r'reglas-conversion', ReglaConversionViewSet, basename='reglas-conversion')
router.register(r'archivos-carga', ArchivoCargaViewSet, basename='archivos-carga')
router.register(r'detalle-carga', DetalleCargaViewSet, basename='detalle-carga')
router.register(r'procesos-conversion', ProcesoConversionViewSet, basename='procesos-conversion')
router.register(r'calificaciones-tributarias', CalificacionTributariaViewSet, basename='calificaciones-tributarias')
router.register(r'auditoria-cambios', AuditoriaCambioViewSet, basename='auditoria-cambios')
router.register(r'bitacora-sistema', BitacoraSistemaViewSet, basename='bitacora-sistema')
router = DefaultRouter()
router.register(r'documentos', DocumentoDigitalViewSet, basename='documentos')
urlpatterns = [
    path('', include(router.urls)),
    path('web/documentos/', views.documentos_lista_view, name='documentos_lista'),
    path('web/documentos/nuevo/', views.documento_pdf_form_view, name='documento_pdf_form'),
    path('documentos/<int:pk>/procesar/', views.documento_procesar_view, name='documento_procesar_view'),  
 ]