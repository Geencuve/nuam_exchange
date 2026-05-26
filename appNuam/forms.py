from django import forms
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
    DocumentoDigital,
    PerfilTributario, 
    NormativaConfig,
    ObligacionTributariaProgramada,
    PlantillaExportacionTributaria
)


class BaseStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs["class"] = "form-control"
            else:
                field.widget.attrs["class"] = "form-control"


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su usuario"
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su contraseña"
        })
    )


class RolForm(BaseStyledForm):
    class Meta:
        model = Rol
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }


class UsuarioForm(BaseStyledForm):
    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Ingrese contraseña"})
    )

    class Meta:
        model = Usuario
        fields = [
            "nombre_completo",
            "username",
            "email",
            "estado",
            "ultimo_acceso",
        ]
        widgets = {
            "ultimo_acceso": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class UsuarioRolForm(BaseStyledForm):
    class Meta:
        model = UsuarioRol
        fields = ["usuario", "rol"]


class SesionAccesoForm(BaseStyledForm):
    class Meta:
        model = SesionAcceso
        fields = [
            "usuario",
            "fecha_login",
            "fecha_logout",
            "ip_origen",
            "user_agent",
            "estado",
        ]
        widgets = {
            "fecha_login": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "fecha_logout": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "user_agent": forms.Textarea(attrs={"rows": 2}),
        }


class PaisForm(BaseStyledForm):
    class Meta:
        model = Pais
        fields = ["nombre", "codigo_iso", "activo"]


class NormativaTributariaForm(BaseStyledForm):
    class Meta:
        model = NormativaTributaria
        fields = [
            "pais",
            "nombre_normativa",
            "version_normativa",
            "descripcion",
            "vigente_desde",
            "vigente_hasta",
            "estado",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "vigente_desde": forms.DateInput(attrs={"type": "date"}),
            "vigente_hasta": forms.DateInput(attrs={"type": "date"}),
        }


class InstrumentoFinancieroForm(BaseStyledForm):
    class Meta:
        model = InstrumentoFinanciero
        fields = [
            "pais",
            "rut_emisor",
            "codigo_instrumento",
            "nombre_instrumento",
            "tipo_instrumento",
            "estado",
        ]


class FactorTributarioForm(BaseStyledForm):
    class Meta:
        model = FactorTributario
        fields = [
            "pais",
            "normativa",
            "nombre_factor",
            "valor_factor",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "creado_por",
        ]
        widgets = {
            "valor_factor": forms.NumberInput(attrs={"step": "0.000001"}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }


class ReglaConversionForm(BaseStyledForm):
    class Meta:
        model = ReglaConversion
        fields = [
            "pais",
            "normativa",
            "nombre_regla",
            "descripcion",
            "condicion_aplicable",
            "formula_aplicable",
            "prioridad",
            "activa",
            "creado_por",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "condicion_aplicable": forms.Textarea(attrs={"rows": 3}),
            "formula_aplicable": forms.Textarea(attrs={"rows": 3}),
            "prioridad": forms.NumberInput(attrs={"min": 1}),
        }


class ArchivoCargaForm(BaseStyledForm):
    archivo = forms.FileField(
        label="Archivo",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = ArchivoCarga
        fields = [
            "usuario",
            "pais",
            "nombre_archivo",
            "ruta_archivo",
            "tipo_archivo",
            "total_registros",
            "registros_ok",
            "registros_error",
            "estado_proceso",
            "observaciones",
            "fecha_procesamiento",
        ]
        widgets = {
            "observaciones": forms.Textarea(attrs={"rows": 3}),
            "fecha_procesamiento": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class DetalleCargaForm(BaseStyledForm):
    class Meta:
        model = DetalleCarga
        fields = [
            "archivo",
            "numero_fila",
            "dato_original",
            "estado_validacion",
            "mensaje_error",
        ]
        widgets = {
            "dato_original": forms.Textarea(attrs={"rows": 3}),
            "mensaje_error": forms.Textarea(attrs={"rows": 2}),
        }


class ProcesoConversionForm(BaseStyledForm):
    class Meta:
        model = ProcesoConversion
        fields = [
            "archivo",
            "usuario",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "total_procesados",
            "total_error",
            "mensaje_resumen",
        ]
        widgets = {
            "fecha_inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "fecha_fin": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "mensaje_resumen": forms.Textarea(attrs={"rows": 3}),
        }


class CalificacionTributariaForm(BaseStyledForm):
    class Meta:
        model = CalificacionTributaria
        fields = [
            "instrumento",
            "pais",
            "normativa",
            "factor",
            "archivo",
            "monto_origen",
            "resultado_factor",
            "valor_calculado",
            "fecha_calculo",
            "vigencia_desde",
            "vigencia_hasta",
            "estado",
            "observaciones",
            "creado_por",
        ]
        widgets = {
            "monto_origen": forms.NumberInput(attrs={"step": "0.0001"}),
            "resultado_factor": forms.NumberInput(attrs={"step": "0.000001"}),
            "valor_calculado": forms.NumberInput(attrs={"step": "0.0001"}),
            "fecha_calculo": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "vigencia_desde": forms.DateInput(attrs={"type": "date"}),
            "vigencia_hasta": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }


class AuditoriaCambioForm(BaseStyledForm):
    class Meta:
        model = AuditoriaCambio
        fields = [
            "tabla_afectada",
            "registro_id",
            "usuario",
            "accion",
            "valor_anterior",
            "valor_nuevo",
            "ip_origen",
            "observacion",
        ]
        widgets = {
            "valor_anterior": forms.Textarea(attrs={"rows": 3}),
            "valor_nuevo": forms.Textarea(attrs={"rows": 3}),
            "observacion": forms.Textarea(attrs={"rows": 2}),
        }


class BitacoraSistemaForm(BaseStyledForm):
    class Meta:
        model = BitacoraSistema
        fields = [
            "nivel",
            "modulo",
            "mensaje",
            "detalle",
            "usuario",
        ]
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows": 2}),
            "detalle": forms.Textarea(attrs={"rows": 3}),
        }


class BusquedaCalificacionForm(forms.Form):
    rut_emisor = forms.CharField(
        required=False,
        label="RUT Emisor",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese RUT"
        })
    )
    codigo_instrumento = forms.CharField(
        required=False,
        label="Código Instrumento",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese código"
        })
    )
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all(),
        required=False,
        empty_label="Seleccione país",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[("", "Seleccione estado")] + CalificacionTributaria.ESTADO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )


class FiltroAuditoriaForm(forms.Form):
    tabla_afectada = forms.CharField(
        required=False,
        label="Tabla afectada",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: factores_tributarios"
        })
    )
    accion = forms.ChoiceField(
        required=False,
        choices=[("", "Seleccione acción")] + AuditoriaCambio.ACCION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.all(),
        required=False,
        empty_label="Seleccione usuario",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )


class DocumentoPDFForm(forms.ModelForm):
    class Meta:
        model = DocumentoDigital
        fields = ['usuario', 'pais', 'archivo', 'observacion']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'pais': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'observacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese una observación opcional'
            }),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo:
            raise forms.ValidationError('Debe seleccionar un archivo PDF.')

        if not archivo.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Solo se permiten archivos PDF.')

        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError('El PDF no debe superar 10 MB.')

        return archivo