# appNuam/services/use_cases.py
from appNuam.services.tax_rules_engine import TaxRulesEngineService, EngineContext
from appNuam.models import PerfilTributario

def calcular_calificacion_para_usuario(usuario, pais_id, financial_data, periodo='2026-05'):
    perfil = PerfilTributario.objects.get(usuario=usuario)

    engine = TaxRulesEngineService()
    result = engine.execute(
        EngineContext(
            usuario_id=usuario.id,
            pais_id=pais_id,
            periodo=periodo,
            financial_data=financial_data,
            profile_data={
                'regimen': perfil.regimen,
                'actividad': perfil.actividad,
                **perfil.atributos
            }
        )
    )
    return result