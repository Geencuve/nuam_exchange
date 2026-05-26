from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import DocumentoPDFForm, UsuarioForm, PaisForm, CalificacionTributariaForm, NormativaTributariaForm, FactorTributarioForm,ReglaConversionForm, ArchivoCargaForm
from .models import DocumentoDigital, DocumentoExtraido
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DocumentoDigital, DocumentoExtraido
from .serializers import DocumentoDigitalSerializer, DocumentoExtraido
from pypdf import PdfReader
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font
from .models import AuditoriaCambio

from .models import (
    Rol,
    Usuario,
    UsuarioRol,
    SesionAcceso,
    Pais,
    NormativaTributaria,
    InstrumentoFinanciero,
    FactorTributario,
    ReglaConversion,
    ArchivoCarga,
    DetalleCarga,
    ProcesoConversion,
    CalificacionTributaria,
    AuditoriaCambio,
    BitacoraSistema,
)

from .serializers import (
    RolSerializer,
    UsuarioSerializer,
    UsuarioRolSerializer,
    SesionAccesoSerializer,
    PaisSerializer,
    NormativaTributariaSerializer,
    InstrumentoFinancieroSerializer,
    FactorTributarioSerializer,
    ReglaConversionSerializer,
    ArchivoCargaSerializer,
    DetalleCargaSerializer,
    ProcesoConversionSerializer,
    CalificacionTributariaSerializer,
    AuditoriaCambioSerializer,
    BitacoraSistemaSerializer,
)

class DocumentoDigitalViewSet(viewsets.ModelViewSet):
    queryset = DocumentoDigital.objects.all().order_by('-fecha_subida')
    serializer_class = DocumentoDigitalSerializer

    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        documento = self.get_object()
        documento.estado = 'procesando'
        documento.save()

        texto_ocr = "Texto extraído de ejemplo"
        extraido, created = DocumentoExtraido.objects.update_or_create(
            documento=documento,
            defaults={
                'texto_extraido': texto_ocr,
                'rut': '11111111-1',
                'pais': 'Chile',
                'monto': 1000000,
                'instrumento': 'Bono'
            }
        )

        documento.estado = 'extraido'
        documento.save()

        return Response({
            'mensaje': 'Documento procesado correctamente',
            'documento_id': documento.id
        }, status=status.HTTP_200_OK)


def dashboard_view(request):
    return render(request, "appNuam/dashboard.html")


def login_view(request):
    return render(request, "appNuam/login.html")


def usuarios_lista_view(request):
    usuarios = Usuario.objects.all().order_by('id')
    return render(request, 'appNuam/usuarios_lista.html', {
        'usuarios': usuarios
    })


def usuario_form_view(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            else:
                usuario.set_password('123456')

            usuario.save()
            return redirect('usuarios_lista')
    else:
        form = UsuarioForm()

    return render(request, 'appNuam/usuario_form.html', {'form': form})

def paises_lista_view(request):
    paises = Pais.objects.all().order_by('id')
    return render(request, 'appNuam/paises_lista.html', {
        'paises': paises
    })


def pais_form_view(request):
    if request.method == 'POST':
        form = PaisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paises_lista')
    else:
        form = PaisForm()

    return render(request, 'appNuam/pais_form.html', {
        'form': form
    })


def normativas_lista_view(request):
    normativas = NormativaTributaria.objects.select_related('pais').all().order_by('-vigente_desde', 'id')
    return render(request, 'appNuam/normativas_lista.html', {
        'normativas': normativas
    })


def normativa_form_view(request):
    if request.method == 'POST':
        form = NormativaTributariaForm(request.POST)
        if form.is_valid():
            normativa = form.save()
            return redirect('normativa_configurar', normativa_id=normativa.id)
    else:
        form = NormativaTributariaForm()

    return render(request, 'appNuam/normativa_form.html', {
        'form': form
    })


from django.shortcuts import render, get_object_or_404
from .models import NormativaTributaria, FactorTributario, ReglaConversion

def normativa_configurar_view(request, normativa_id):
    normativa = get_object_or_404(
        NormativaTributaria.objects.select_related('pais'),
        pk=normativa_id
    )

    factores = FactorTributario.objects.filter(
        normativa=normativa
    ).select_related('pais', 'creado_por').order_by('-fecha_inicio', '-id')

    reglas = ReglaConversion.objects.filter(
        normativa=normativa
    ).select_related('pais', 'creado_por').order_by('prioridad', 'id')

    total_factores = factores.count()
    factores_vigentes = factores.filter(estado='VIGENTE').count()
    total_reglas = reglas.count()
    reglas_activas = reglas.filter(activa=True).count()
    reglas_sin_formula = reglas.filter(formula_aplicable__isnull=True).count() + reglas.filter(formula_aplicable='').count()
    total_calificaciones = CalificacionTributaria.objects.filter(normativa=normativa).count()

    return render(request, 'appNuam/normativa_configurar.html', {
        'normativa': normativa,
        'factores': factores,
        'reglas': reglas,
        'total_factores': total_factores,
        'factores_vigentes': factores_vigentes,
        'total_reglas': total_reglas,
        'reglas_activas': reglas_activas,
        'reglas_sin_formula': reglas_sin_formula,
        'total_calificaciones': total_calificaciones,
    })


def regla_form_view(request):
    normativa_id = request.GET.get('normativa_id') or request.POST.get('normativa_id')
    normativa = None

    if normativa_id:
        normativa = get_object_or_404(NormativaTributaria, pk=normativa_id)

    if request.method == 'POST':
        form = ReglaConversionForm(request.POST)
        if form.is_valid():
            regla = form.save(commit=False)

            if normativa:
                regla.normativa = normativa
                regla.pais = normativa.pais

            regla.save()

            if normativa:
                return redirect('normativa_configurar', normativa_id=normativa.id)

            return redirect('reglas_lista')
    else:
        initial = {}
        if normativa:
            initial['normativa'] = normativa
            initial['pais'] = normativa.pais

        form = ReglaConversionForm(initial=initial)

    return render(request, 'appNuam/regla_form.html', {
        'form': form,
        'normativa': normativa,
    })


def factores_lista_view(request):
    factores = (
        FactorTributario.objects
        .select_related('pais', 'normativa', 'creado_por')
        .all()
        .order_by('-fecha_inicio', '-id')
    )

    return render(request, 'appNuam/factores_lista.html', {
        'factores': factores
    })


def factores_form_view(request):
    normativa_id = request.GET.get('normativa_id') or request.POST.get('normativa_id')
    normativa = None

    if normativa_id:
        normativa = get_object_or_404(NormativaTributaria, pk=normativa_id)

    if request.method == 'POST':
        form = FactorTributarioForm(request.POST)
        if form.is_valid():
            factor = form.save(commit=False)

            if normativa:
                factor.normativa = normativa
                factor.pais = normativa.pais

            factor.save()

            if normativa:
                return redirect('normativa_configurar', normativa_id=normativa.id)

            return redirect('factores_lista')
    else:
        initial = {}
        if normativa:
            initial['normativa'] = normativa
            initial['pais'] = normativa.pais

        form = FactorTributarioForm(initial=initial)

    return render(request, 'appNuam/factores_form.html', {
        'form': form,
        'normativa': normativa,
    })


def reglas_lista_view(request):
    reglas = (
        ReglaConversion.objects
        .select_related('pais', 'normativa', 'creado_por')
        .all()
        .order_by('prioridad', 'id')
    )

    return render(request, 'appNuam/reglas_lista.html', {
        'reglas': reglas
    })


def archivo_carga_form_view(request):
    if request.method == 'POST':
        form = ArchivoCargaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_carga = form.save(commit=False)

            archivo_subido = request.FILES.get('archivo')
            if archivo_subido:
                archivo_carga.nombre_archivo = archivo_subido.name
                archivo_carga.ruta_archivo = archivo_subido.name

            archivo_carga.save()
            return redirect('archivos_carga_lista')
    else:
        form = ArchivoCargaForm()

    return render(request, 'appNuam/archivo_carga_form.html', {
        'form': form
    })


def archivos_carga_lista_view(request):
    archivos = (
        ArchivoCarga.objects
        .select_related('usuario', 'pais')
        .all()
        .order_by('-fecha_carga', '-id')
    )

    return render(request, 'appNuam/archivos_carga_lista.html', {
        'archivos': archivos
    })

def calificaciones_lista_view(request):
    calificaciones = (
        CalificacionTributaria.objects
        .select_related('instrumento', 'pais', 'normativa', 'factor', 'archivo', 'creado_por')
        .all()
        .order_by('-fecha_calculo', '-id')
    )

    return render(request, 'appNuam/calificaciones_lista.html', {
        'calificaciones': calificaciones
    })


def calificacion_form_view(request):
    if request.method == 'POST':
        form = CalificacionTributariaForm(request.POST)
        if form.is_valid():
            calificacion = form.save()
            return redirect('calificaciones_lista')
    else:
        form = CalificacionTributariaForm()

    return render(request, 'appNuam/calificacion_form.html', {
        'form': form
    })




def auditoria_lista_view(request):
    auditorias = (
        AuditoriaCambio.objects
        .select_related('usuario')
        .all()
        .order_by('-fecha_evento', '-id')
    )

    return render(request, 'appNuam/auditoria_lista.html', {
        'auditorias': auditorias
    })






class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class RolViewSet(BaseModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["id", "nombre", "created_at"]
    ordering = ["nombre"]


class UsuarioViewSet(BaseModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    search_fields = ["nombre_completo", "username", "email", "estado"]
    ordering_fields = ["id", "nombre_completo", "username", "email", "created_at"]
    ordering = ["nombre_completo"]

    @action(detail=True, methods=["get"])
    def roles(self, request, pk=None):
        usuario = self.get_object()
        roles = usuario.roles_asignados.select_related("rol")
        data = [{"id": r.rol.id, "nombre": r.rol.nombre} for r in roles]
        return Response(data)

    @action(detail=True, methods=["post"])
    def cambiar_estado(self, request, pk=None):
        usuario = self.get_object()
        nuevo_estado = request.data.get("estado")
        estados_validos = ["ACTIVO", "INACTIVO", "BLOQUEADO"]

        if nuevo_estado not in estados_validos:
            return Response(
                {"detail": "Estado no válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.estado = nuevo_estado
        usuario.save()
        return Response({"detail": "Estado actualizado correctamente."})


class UsuarioRolViewSet(BaseModelViewSet):
    queryset = UsuarioRol.objects.select_related("usuario", "rol").all()
    serializer_class = UsuarioRolSerializer
    search_fields = ["usuario__username", "usuario__nombre_completo", "rol__nombre"]
    ordering_fields = ["id", "asignado_en"]
    ordering = ["-asignado_en"]


class SesionAccesoViewSet(BaseModelViewSet):
    queryset = SesionAcceso.objects.select_related("usuario").all()
    serializer_class = SesionAccesoSerializer
    search_fields = ["usuario__username", "usuario__nombre_completo", "estado", "ip_origen"]
    ordering_fields = ["id", "fecha_login", "fecha_logout"]
    ordering = ["-fecha_login"]

    @action(detail=False, methods=["get"])
    def abiertas(self, request):
        sesiones = self.get_queryset().filter(estado="ABIERTA")
        serializer = self.get_serializer(sesiones, many=True)
        return Response(serializer.data)


class PaisViewSet(BaseModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    search_fields = ["nombre", "codigo_iso"]
    ordering_fields = ["id", "nombre", "codigo_iso", "created_at"]
    ordering = ["nombre"]


class NormativaTributariaViewSet(BaseModelViewSet):
    queryset = NormativaTributaria.objects.select_related("pais").all()
    serializer_class = NormativaTributariaSerializer
    search_fields = ["nombre_normativa", "version_normativa", "estado", "pais__nombre"]
    ordering_fields = ["id", "nombre_normativa", "vigente_desde", "vigente_hasta", "created_at"]
    ordering = ["-vigente_desde"]

    def get_queryset(self):
        queryset = super().get_queryset()
        pais_id = self.request.query_params.get("pais_id")
        estado = self.request.query_params.get("estado")

        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class InstrumentoFinancieroViewSet(BaseModelViewSet):
    queryset = InstrumentoFinanciero.objects.select_related("pais").all()
    serializer_class = InstrumentoFinancieroSerializer
    search_fields = [
        "rut_emisor",
        "codigo_instrumento",
        "nombre_instrumento",
        "tipo_instrumento",
        "pais__nombre",
    ]
    ordering_fields = ["id", "codigo_instrumento", "nombre_instrumento", "created_at"]
    ordering = ["codigo_instrumento"]

    def get_queryset(self):
        queryset = super().get_queryset()
        pais_id = self.request.query_params.get("pais_id")
        estado = self.request.query_params.get("estado")

        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class FactorTributarioViewSet(BaseModelViewSet):
    queryset = FactorTributario.objects.select_related("pais", "normativa", "creado_por").all()
    serializer_class = FactorTributarioSerializer
    search_fields = [
        "nombre_factor",
        "estado",
        "pais__nombre",
        "normativa__nombre_normativa",
        "creado_por__username",
    ]
    ordering_fields = ["id", "nombre_factor", "valor_factor", "fecha_inicio", "fecha_fin", "created_at"]
    ordering = ["-fecha_inicio"]

    def get_queryset(self):
        queryset = super().get_queryset()
        pais_id = self.request.query_params.get("pais_id")
        normativa_id = self.request.query_params.get("normativa_id")
        estado = self.request.query_params.get("estado")

        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        if normativa_id:
            queryset = queryset.filter(normativa_id=normativa_id)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    @action(detail=False, methods=["get"])
    def vigentes(self, request):
        queryset = self.get_queryset().filter(estado="VIGENTE")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReglaConversionViewSet(BaseModelViewSet):
    queryset = ReglaConversion.objects.select_related("pais", "normativa", "creado_por").all()
    serializer_class = ReglaConversionSerializer
    search_fields = [
        "nombre_regla",
        "descripcion",
        "pais__nombre",
        "normativa__nombre_normativa",
        "creado_por__username",
    ]
    ordering_fields = ["id", "nombre_regla", "prioridad", "created_at"]
    ordering = ["prioridad", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        pais_id = self.request.query_params.get("pais_id")
        normativa_id = self.request.query_params.get("normativa_id")
        activa = self.request.query_params.get("activa")

        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        if normativa_id:
            queryset = queryset.filter(normativa_id=normativa_id)
        if activa is not None:
            if activa.lower() == "true":
                queryset = queryset.filter(activa=True)
            elif activa.lower() == "false":
                queryset = queryset.filter(activa=False)

        return queryset

    @action(detail=False, methods=["get"])
    def activas(self, request):
        queryset = self.get_queryset().filter(activa=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ArchivoCargaViewSet(BaseModelViewSet):
    queryset = ArchivoCarga.objects.select_related("usuario", "pais").all()
    serializer_class = ArchivoCargaSerializer
    search_fields = [
        "nombre_archivo",
        "tipo_archivo",
        "estado_proceso",
        "usuario__username",
        "pais__nombre",
    ]
    ordering_fields = ["id", "fecha_carga", "fecha_procesamiento", "estado_proceso"]
    ordering = ["-fecha_carga"]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario_id = self.request.query_params.get("usuario_id")
        pais_id = self.request.query_params.get("pais_id")
        estado = self.request.query_params.get("estado")

        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        if estado:
            queryset = queryset.filter(estado_proceso=estado)

        return queryset

    @action(detail=True, methods=["get"])
    def detalles(self, request, pk=None):
        archivo = self.get_object()
        detalles = archivo.detalles.all().order_by("numero_fila")
        serializer = DetalleCargaSerializer(detalles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pendientes(self, request):
        queryset = self.get_queryset().filter(estado_proceso="PENDIENTE")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DetalleCargaViewSet(BaseModelViewSet):
    queryset = DetalleCarga.objects.select_related("archivo").all()
    serializer_class = DetalleCargaSerializer
    search_fields = ["estado_validacion", "mensaje_error", "archivo__nombre_archivo"]
    ordering_fields = ["id", "numero_fila", "creado_en"]
    ordering = ["archivo_id", "numero_fila"]

    def get_queryset(self):
        queryset = super().get_queryset()
        archivo_id = self.request.query_params.get("archivo_id")
        estado = self.request.query_params.get("estado")

        if archivo_id:
            queryset = queryset.filter(archivo_id=archivo_id)
        if estado:
            queryset = queryset.filter(estado_validacion=estado)

        return queryset


class ProcesoConversionViewSet(BaseModelViewSet):
    queryset = ProcesoConversion.objects.select_related("archivo", "usuario").all()
    serializer_class = ProcesoConversionSerializer
    search_fields = ["estado", "usuario__username", "archivo__nombre_archivo"]
    ordering_fields = ["id", "fecha_inicio", "fecha_fin", "estado"]
    ordering = ["-fecha_inicio"]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario_id = self.request.query_params.get("usuario_id")
        archivo_id = self.request.query_params.get("archivo_id")
        estado = self.request.query_params.get("estado")

        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if archivo_id:
            queryset = queryset.filter(archivo_id=archivo_id)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class CalificacionTributariaViewSet(BaseModelViewSet):
    queryset = CalificacionTributaria.objects.select_related(
        "instrumento", "pais", "normativa", "factor", "archivo", "creado_por"
    ).all()
    serializer_class = CalificacionTributariaSerializer
    search_fields = [
        "instrumento__codigo_instrumento",
        "instrumento__nombre_instrumento",
        "instrumento__rut_emisor",
        "pais__nombre",
        "estado",
    ]
    ordering_fields = [
        "id",
        "fecha_calculo",
        "vigencia_desde",
        "vigencia_hasta",
        "valor_calculado",
        "created_at",
    ]
    ordering = ["-fecha_calculo"]

    def get_queryset(self):
        queryset = super().get_queryset()
        pais_id = self.request.query_params.get("pais_id")
        instrumento_id = self.request.query_params.get("instrumento_id")
        normativa_id = self.request.query_params.get("normativa_id")
        estado = self.request.query_params.get("estado")

        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        if instrumento_id:
            queryset = queryset.filter(instrumento_id=instrumento_id)
        if normativa_id:
            queryset = queryset.filter(normativa_id=normativa_id)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    @action(detail=False, methods=["get"])
    def vigentes(self, request):
        queryset = self.get_queryset().filter(estado="VIGENTE")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AuditoriaCambioViewSet(BaseModelViewSet):
    queryset = AuditoriaCambio.objects.select_related("usuario").all()
    serializer_class = AuditoriaCambioSerializer
    search_fields = ["tabla_afectada", "accion", "usuario__username", "ip_origen"]
    ordering_fields = ["id", "fecha_evento", "tabla_afectada", "accion"]
    ordering = ["-fecha_evento"]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario_id = self.request.query_params.get("usuario_id")
        tabla = self.request.query_params.get("tabla")
        accion = self.request.query_params.get("accion")

        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if tabla:
            queryset = queryset.filter(tabla_afectada__icontains=tabla)
        if accion:
            queryset = queryset.filter(accion=accion)

        return queryset


class BitacoraSistemaViewSet(BaseModelViewSet):
    queryset = BitacoraSistema.objects.select_related("usuario").all()
    serializer_class = BitacoraSistemaSerializer
    search_fields = ["nivel", "modulo", "mensaje", "usuario__username"]
    ordering_fields = ["id", "fecha_evento", "nivel", "modulo"]
    ordering = ["-fecha_evento"]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario_id = self.request.query_params.get("usuario_id")
        nivel = self.request.query_params.get("nivel")
        modulo = self.request.query_params.get("modulo")

        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if nivel:
            queryset = queryset.filter(nivel=nivel)
        if modulo:
            queryset = queryset.filter(modulo__icontains=modulo)

        return queryset



def documentos_lista_view(request):
    documentos = DocumentoDigital.objects.all().order_by('-fecha_subida')
    return render(request, 'appNuam/documentos_lista.html', {
        'documentos': documentos
    })


def documento_pdf_form_view(request):
    if request.method == 'POST':
        form = DocumentoPDFForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.nombre_archivo = documento.archivo.name
            documento.tipo_documento = 'pdf'
            documento.estado = 'subido'
            documento.save()

            messages.success(request, 'PDF cargado correctamente.')
            return redirect('documentos_lista')
    else:
        form = DocumentoPDFForm()

    return render(request, 'appNuam/documento_pdf_form.html', {
        'form': form
    })


def documento_procesar_view(request, pk):
    documento = get_object_or_404(DocumentoDigital, pk=pk)

    try:
        documento.estado = 'procesando'
        documento.save()

        reader = PdfReader(documento.archivo.path)
        texto_paginas = []

        for pagina in reader.pages:
            texto = pagina.extract_text()
            if texto:
                texto_paginas.append(texto)

        texto_final = '\n'.join(texto_paginas).strip()

        DocumentoExtraido.objects.update_or_create(
            documento=documento,
            defaults={
                'textoextraido': texto_final if texto_final else 'No se pudo extraer texto del PDF.'
            }
        )

        documento.estado = 'extraido'
        documento.save()

        messages.success(request, 'PDF procesado correctamente.')

    except Exception as e:
        documento.estado = 'error'
        documento.observacion = f'Error al procesar PDF: {str(e)}'
        documento.save()
        messages.error(request, 'Ocurrió un error al procesar el PDF.')

    return redirect('archivos_carga_lista')


def auditoria_exportar_view(request):
    auditorias = (
        AuditoriaCambio.objects
        .select_related('usuario')
        .all()
        .order_by('-fecha_evento', '-id')
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Auditoria"

    encabezados = [
        "ID",
        "Tabla afectada",
        "Registro ID",
        "Usuario",
        "Acción",
        "IP origen",
        "Fecha evento",
        "Observación",
    ]
    ws.append(encabezados)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    for auditoria in auditorias:
        ws.append([
            auditoria.id,
            auditoria.tabla_afectada,
            auditoria.registro_id,
            auditoria.usuario.username if auditoria.usuario else "",
            auditoria.accion,
            auditoria.iporigen or "",
            auditoria.fecha_evento.strftime("%Y-%m-%d %H:%M:%S") if auditoria.fecha_evento else "",
            auditoria.observacion or "",
        ])

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 22
    ws.column_dimensions["H"].width = 40

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="auditoria_cambios.xlsx"'

    wb.save(response)
    return response