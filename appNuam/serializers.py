from rest_framework import serializers
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

from .models import DocumentoDigital, DocumentoExtraido, DocumentoValidacion

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = "__all__"


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {
            "password_hash": {"write_only": True}
        }


class UsuarioRolSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre_completo", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    rol_nombre = serializers.CharField(source="rol.nombre", read_only=True)

    class Meta:
        model = UsuarioRol
        fields = "__all__"


class SesionAccesoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre_completo", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = SesionAcceso
        fields = "__all__"


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = "__all__"


class NormativaTributariaSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)

    class Meta:
        model = NormativaTributaria
        fields = "__all__"


class InstrumentoFinancieroSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)

    class Meta:
        model = InstrumentoFinanciero
        fields = "__all__"


class FactorTributarioSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)
    normativa_nombre = serializers.CharField(source="normativa.nombre_normativa", read_only=True)
    creado_por_username = serializers.CharField(source="creado_por.username", read_only=True)

    class Meta:
        model = FactorTributario
        fields = "__all__"


class ReglaConversionSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)
    normativa_nombre = serializers.CharField(source="normativa.nombre_normativa", read_only=True)
    creado_por_username = serializers.CharField(source="creado_por.username", read_only=True)

    class Meta:
        model = ReglaConversion
        fields = "__all__"


class ArchivoCargaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)

    class Meta:
        model = ArchivoCarga
        fields = "__all__"


class DetalleCargaSerializer(serializers.ModelSerializer):
    archivo_nombre = serializers.CharField(source="archivo.nombre_archivo", read_only=True)

    class Meta:
        model = DetalleCarga
        fields = "__all__"


class ProcesoConversionSerializer(serializers.ModelSerializer):
    archivo_nombre = serializers.CharField(source="archivo.nombre_archivo", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = ProcesoConversion
        fields = "__all__"


class CalificacionTributariaSerializer(serializers.ModelSerializer):
    instrumento_codigo = serializers.CharField(source="instrumento.codigo_instrumento", read_only=True)
    instrumento_nombre = serializers.CharField(source="instrumento.nombre_instrumento", read_only=True)
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)
    normativa_nombre = serializers.CharField(source="normativa.nombre_normativa", read_only=True)
    factor_nombre = serializers.CharField(source="factor.nombre_factor", read_only=True)
    creado_por_username = serializers.CharField(source="creado_por.username", read_only=True)

    class Meta:
        model = CalificacionTributaria
        fields = "__all__"


class AuditoriaCambioSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = AuditoriaCambio
        fields = "__all__"


class BitacoraSistemaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = BitacoraSistema
        fields = "__all__"




class DocumentoDigitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoDigital
        fields = '__all__'


class DocumentoExtraidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoExtraido
        fields = '__all__'


class DocumentoValidacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoValidacion
        fields = '__all__'