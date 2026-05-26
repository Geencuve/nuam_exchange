from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Rol(TimeStampedModel):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "roles"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        
        return self.nombre


class Usuario(TimeStampedModel):
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
        ("BLOQUEADO", "Bloqueado"),
    ]

    nombre_completo = models.CharField(max_length=150)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=120, unique=True)
    password_hash = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ACTIVO")
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre_completo} ({self.username})"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)


class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="roles_asignados")
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="usuarios_asignados")
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuario_roles"
        verbose_name = "Usuario Rol"
        verbose_name_plural = "Usuario Roles"
        unique_together = ("usuario", "rol")

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"


class SesionAcceso(models.Model):
    ESTADO_CHOICES = [
        ("ABIERTA", "Abierta"),
        ("CERRADA", "Cerrada"),
        ("EXPIRADA", "Expirada"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sesiones")
    fecha_login = models.DateTimeField()
    fecha_logout = models.DateTimeField(blank=True, null=True)
    ip_origen = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ABIERTA")

    class Meta:
        db_table = "sesiones_acceso"
        verbose_name = "Sesión de acceso"
        verbose_name_plural = "Sesiones de acceso"

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_login}"


class Pais(TimeStampedModel):
    nombre = models.CharField(max_length=80, unique=True)
    codigo_iso = models.CharField(max_length=5, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "paises"
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nombre


class NormativaTributaria(TimeStampedModel):
    ESTADO_CHOICES = [
        ("VIGENTE", "Vigente"),
        ("INACTIVA", "Inactiva"),
        ("BORRADOR", "Borrador"),
    ]

    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="normativas")
    nombre_normativa = models.CharField(max_length=150)
    version_normativa = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="VIGENTE")

    class Meta:
        db_table = "normativas_tributarias"
        verbose_name = "Normativa tributaria"
        verbose_name_plural = "Normativas tributarias"
        unique_together = ("pais", "nombre_normativa", "version_normativa")

    def __str__(self):
        return f"{self.nombre_normativa} - {self.version_normativa}"


class InstrumentoFinanciero(TimeStampedModel):
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
    ]

    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="instrumentos")
    rut_emisor = models.CharField(max_length=20)
    codigo_instrumento = models.CharField(max_length=50, unique=True)
    nombre_instrumento = models.CharField(max_length=150)
    tipo_instrumento = models.CharField(max_length=80)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ACTIVO")

    class Meta:
        db_table = "instrumentos_financieros"
        verbose_name = "Instrumento financiero"
        verbose_name_plural = "Instrumentos financieros"

    def __str__(self):
        return f"{self.codigo_instrumento} - {self.nombre_instrumento}"


class FactorTributario(TimeStampedModel):
    ESTADO_CHOICES = [
        ("VIGENTE", "Vigente"),
        ("INACTIVO", "Inactivo"),
    ]

    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="factores")
    normativa = models.ForeignKey(NormativaTributaria, on_delete=models.PROTECT, related_name="factores")
    nombre_factor = models.CharField(max_length=120)
    valor_factor = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(0)])
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="VIGENTE")
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="factores_creados"
    )

    class Meta:
        db_table = "factores_tributarios"
        verbose_name = "Factor tributario"
        verbose_name_plural = "Factores tributarios"

    def __str__(self):
        return f"{self.nombre_factor} - {self.valor_factor}"


class ReglaConversion(TimeStampedModel):
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="reglas_conversion")
    normativa = models.ForeignKey(NormativaTributaria, on_delete=models.PROTECT, related_name="reglas_conversion")
    nombre_regla = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    condicion_aplicable = models.TextField()
    formula_aplicable = models.TextField()
    prioridad = models.PositiveIntegerField(default=1)
    activa = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reglas_creadas"
    )

    class Meta:
        db_table = "reglas_conversion"
        verbose_name = "Regla de conversión"
        verbose_name_plural = "Reglas de conversión"
        ordering = ["prioridad", "id"]

    def __str__(self):
        return self.nombre_regla


class ArchivoCarga(TimeStampedModel):
    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("PROCESANDO", "Procesando"),
        ("PROCESADO", "Procesado"),
        ("PROCESADO_CON_ERRORES", "Procesado con errores"),
        ("RECHAZADO", "Rechazado"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="archivos_cargados")
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="archivos_carga")
    nombre_archivo = models.CharField(max_length=255)
    ruta_archivo = models.CharField(max_length=500)
    tipo_archivo = models.CharField(max_length=20)
    total_registros = models.PositiveIntegerField(default=0)
    registros_ok = models.PositiveIntegerField(default=0)
    registros_error = models.PositiveIntegerField(default=0)
    estado_proceso = models.CharField(max_length=30, choices=ESTADO_CHOICES, default="PENDIENTE")
    observaciones = models.TextField(blank=True, null=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "archivos_carga"
        verbose_name = "Archivo de carga"
        verbose_name_plural = "Archivos de carga"

    def __str__(self):
        return self.nombre_archivo


class DetalleCarga(models.Model):
    ESTADO_CHOICES = [
        ("VALIDO", "Válido"),
        ("ERROR", "Error"),
        ("OMITIDO", "Omitido"),
    ]

    archivo = models.ForeignKey(ArchivoCarga, on_delete=models.CASCADE, related_name="detalles")
    numero_fila = models.PositiveIntegerField()
    dato_original = models.TextField()
    estado_validacion = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    mensaje_error = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "detalle_carga"
        verbose_name = "Detalle de carga"
        verbose_name_plural = "Detalles de carga"
        unique_together = ("archivo", "numero_fila")

    def __str__(self):
        return f"Archivo {self.archivo_id} - fila {self.numero_fila}"


class ProcesoConversion(models.Model):
    ESTADO_CHOICES = [
        ("INICIADO", "Iniciado"),
        ("FINALIZADO", "Finalizado"),
        ("ERROR", "Error"),
        ("PARCIAL", "Parcial"),
    ]

    archivo = models.ForeignKey(ArchivoCarga, on_delete=models.CASCADE, related_name="procesos")
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="procesos_conversion")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="INICIADO")
    total_procesados = models.PositiveIntegerField(default=0)
    total_error = models.PositiveIntegerField(default=0)
    mensaje_resumen = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "procesos_conversion"
        verbose_name = "Proceso de conversión"
        verbose_name_plural = "Procesos de conversión"

    def __str__(self):
        return f"Proceso {self.id} - {self.estado}"


class CalificacionTributaria(TimeStampedModel):
    ESTADO_CHOICES = [
        ("VIGENTE", "Vigente"),
        ("EXPIRADA", "Expirada"),
        ("ANULADA", "Anulada"),
        ("BORRADOR", "Borrador"),
    ]

    instrumento = models.ForeignKey(
        InstrumentoFinanciero,
        on_delete=models.PROTECT,
        related_name="calificaciones"
    )
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="calificaciones")
    normativa = models.ForeignKey(
        NormativaTributaria,
        on_delete=models.PROTECT,
        related_name="calificaciones"
    )
    factor = models.ForeignKey(
        FactorTributario,
        on_delete=models.PROTECT,
        related_name="calificaciones"
    )
    archivo = models.ForeignKey(
        ArchivoCarga,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calificaciones_generadas"
    )
    monto_origen = models.DecimalField(max_digits=18, decimal_places=4, validators=[MinValueValidator(0)])
    resultado_factor = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(0)])
    valor_calculado = models.DecimalField(max_digits=18, decimal_places=4, validators=[MinValueValidator(0)])
    fecha_calculo = models.DateTimeField()
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="VIGENTE")
    observaciones = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="calificaciones_creadas"
    )

    class Meta:
        db_table = "calificaciones_tributarias"
        verbose_name = "Calificación tributaria"
        verbose_name_plural = "Calificaciones tributarias"

    def __str__(self):
        return f"Calificación {self.id} - {self.instrumento.codigo_instrumento}"


class AuditoriaCambio(models.Model):
    ACCION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
    ]

    tabla_afectada = models.CharField(max_length=100)
    registro_id = models.PositiveBigIntegerField()
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="auditorias"
    )
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    valor_anterior = models.JSONField(blank=True, null=True)
    valor_nuevo = models.JSONField(blank=True, null=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    ip_origen = models.CharField(max_length=45, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "auditoria_cambios"
        verbose_name = "Auditoría de cambio"
        verbose_name_plural = "Auditorías de cambios"

    def __str__(self):
        return f"{self.tabla_afectada} - {self.accion}"


class BitacoraSistema(models.Model):
    NIVEL_CHOICES = [
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default="INFO")
    modulo = models.CharField(max_length=80)
    mensaje = models.TextField()
    detalle = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="eventos_bitacora"
    )
    fecha_evento = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitacora_sistema"
        verbose_name = "Bitácora del sistema"
        verbose_name_plural = "Bitácora del sistema"

    def __str__(self):
        return f"{self.nivel} - {self.modulo}"



class DocumentoDigital(models.Model):
    TIPO_CHOICES = [
        ('pdf', 'PDF'),
        ('imagen', 'Imagen'),
        ('scan', 'Escaneo'),
    ]

    ESTADO_CHOICES = [
        ('subido', 'Subido'),
        ('procesando', 'Procesando'),
        ('extraido', 'Extraído'),
        ('validado', 'Validado'),
        ('error', 'Error'),
    ]

    usuario = models.ForeignKey('Usuario', on_delete=models.PROTECT, related_name='documentos_subidos')
    pais = models.ForeignKey('Pais', on_delete=models.PROTECT, related_name='documentos', null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='documentos_pdf/')
    tipo_documento = models.CharField(max_length=20, choices=TIPO_CHOICES, default='pdf')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='subido')
    observacion = models.TextField(blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_digitales'
        verbose_name = 'Documento digital'
        verbose_name_plural = 'Documentos digitales'

    def __str__(self):
        return self.nombre_archivo


class DocumentoExtraido(models.Model):
    documento = models.OneToOneField(DocumentoDigital, on_delete=models.CASCADE, related_name='extraccion')
    texto_extraido = models.TextField()
    rut = models.CharField(max_length=20, blank=True, null=True)
    instrumento = models.CharField(max_length=120, blank=True, null=True)
    monto = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    fecha_extraccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_extraidos'

    def __str__(self):
        return f"Extracción {self.documento_id}"


class DocumentoValidacion(models.Model):
    documento = models.ForeignKey(DocumentoDigital, on_delete=models.CASCADE)
    usuario_validador = models.ForeignKey(User, on_delete=models.CASCADE)
    campo = models.CharField(max_length=100)
    valor_original = models.TextField(blank=True, null=True)
    valor_corregido = models.TextField(blank=True, null=True)
    fecha_validacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Validación {self.campo} - {self.documento.id}"
    

class PerfilTributario(models.Model):
    REGIMEN_CHOICES = (
        ('GENERAL', 'General'),
        ('SIMPLIFICADO', 'Simplificado'),
        ('ESPECIAL', 'Especial'),
    )

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfiltributario')
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name='perfilestributarios')
    regimen = models.CharField(max_length=30, choices=REGIMEN_CHOICES)
    actividad = models.CharField(max_length=120, blank=True, null=True)
    atributos = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'perfilestributarios'

class NormativaConfig(models.Model):
    TIPO_REGLA_CHOICES = (
        ('CALCULO', 'Cálculo'),
        ('VALIDACION', 'Validación'),
        ('SCHEDULING', 'Scheduling'),
        ('EXPORTACION', 'Exportación'),
    )

    normativa = models.ForeignKey(NormativaTributaria, on_delete=models.CASCADE, related_name='configs')
    regla = models.ForeignKey(ReglaConversion, on_delete=models.SET_NULL, null=True, blank=True, related_name='configs')
    codigo = models.CharField(max_length=80)
    nombre = models.CharField(max_length=150)
    tiporegla = models.CharField(max_length=20, choices=TIPO_REGLA_CHOICES)
    version = models.CharField(max_length=30, default='1.0')
    activa = models.BooleanField(default=True)
    prioridad = models.PositiveIntegerField(default=1)
    config = models.JSONField(default=dict)
    vigentedesde = models.DateField()
    vigentehasta = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'normativas_config'
        ordering = ['tiporegla', 'prioridad', 'id']

class ObligacionTributariaProgramada(models.Model):
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('GENERADA', 'Generada'),
        ('CUMPLIDA', 'Cumplida'),
        ('VENCIDA', 'Vencida'),
    )

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='obligacionestributarias')
    perfil = models.ForeignKey(PerfilTributario, on_delete=models.PROTECT, related_name='obligaciones')
    normativa = models.ForeignKey(NormativaTributaria, on_delete=models.PROTECT, related_name='obligacionesprogramadas')
    codigoobligacion = models.CharField(max_length=80)
    nombreobligacion = models.CharField(max_length=150)
    periodicidad = models.CharField(max_length=20)
    fechavencimiento = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'obligacionestributariasprogramadas'

class PlantillaExportacionTributaria(models.Model):
    FORMATO_CHOICES = (
        ('XML', 'XML'),
        ('JSON', 'JSON'),
    )

    normativa = models.ForeignKey(NormativaTributaria, on_delete=models.CASCADE, related_name='plantillasexportacion')
    codigo = models.CharField(max_length=80)
    nombre = models.CharField(max_length=150)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    schema = models.JSONField(default=dict)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'plantillasexportaciontributaria'


