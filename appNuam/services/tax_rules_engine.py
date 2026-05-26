# appNuam/services/tax_rules_engine.py
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Any, Dict, List

from django.db.models import Q

from appNuam.models import NormativaTributaria
from appNuam.models import (
    PerfilTributario,
    NormativaConfig,
    ObligacionTributariaProgramada,
    PlantillaExportacionTributaria,
)

class TaxRuleValidationError(Exception):
    def __init__(self, code: str, message: str, payload: dict | None = None):
        self.code = code
        self.message = message
        self.payload = payload or {}
        super().__init__(message)

@dataclass
class EngineContext:
    usuario_id: int
    pais_id: int
    periodo: str
    financial_data: Dict[str, Any]
    profile_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EngineResult:
    normativa_id: int | None = None
    calculos: Dict[str, Any] = field(default_factory=dict)
    validaciones: List[Dict[str, Any]] = field(default_factory=list)
    obligaciones: List[Dict[str, Any]] = field(default_factory=list)
    exportables: List[Dict[str, Any]] = field(default_factory=list)
    errores: List[Dict[str, Any]] = field(default_factory=list)

class SafeExpressionEvaluator:
    ALLOWED_NAMES = {
        'Decimal': Decimal,
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
    }

    def evaluate(self, expression: str, values: Dict[str, Any]) -> Any:
        sandbox = dict(self.ALLOWED_NAMES)
        sandbox.update(values)
        return eval(expression, {"__builtins__": {}}, sandbox)

class CalculationRuleExecutor:
    def __init__(self, evaluator=None):
        self.evaluator = evaluator or SafeExpressionEvaluator()

    def execute(self, rule_config: dict, context: EngineContext, result: EngineResult):
        formula = rule_config.get('formula', {})
        params = rule_config.get('params', {})
        variables = {}

        for alias, source in formula.get('variables', {}).items():
            variables[alias] = self._resolve_source(source, context, result, params)

        raw = self.evaluator.evaluate(formula['expression'], variables)
        rounding = formula.get('rounding', 2)
        final_value = Decimal(str(raw)).quantize(Decimal('1.' + ('0' * rounding)), rounding=ROUND_HALF_UP)

        result.calculos[rule_config.get('codigo', 'resultado')] = final_value
        result.calculos.update({
            'ultimo_resultado': final_value
        })

    def _resolve_source(self, source: str, context: EngineContext, result: EngineResult, params: dict):
        if source.startswith('financial.'):
            return context.financial_data.get(source.split('.', 1)[1])
        if source.startswith('profile.'):
            return context.profile_data.get(source.split('.', 1)[1])
        if source.startswith('params.'):
            return params.get(source.split('.', 1)[1])
        if source.startswith('results.'):
            return result.calculos.get(source.split('.', 1)[1])
        return None

class ValidationRuleExecutor:
    def __init__(self, evaluator=None):
        self.evaluator = evaluator or SafeExpressionEvaluator()

    def execute(self, rule_config: dict, context: EngineContext, result: EngineResult):
        exceptions = rule_config.get('exceptions', [])
        skipped = set()

        for exc in exceptions:
            condition = exc.get('condition')
            if condition and self.evaluator.evaluate(condition, {
                'profile': context.profile_data,
                'financial': context.financial_data,
                'results': result.calculos,
            }):
                skipped.update(exc.get('skip_validations', []))

        for item in rule_config.get('validations', []):
            code = item['error_code']
            if code in skipped:
                continue

            current_value = context.financial_data.get(item['field'])
            expected = item['value']
            operator = item['operator']

            if not self._compare(current_value, operator, expected):
                error = {
                    'code': code,
                    'message': item['message'],
                    'field': item['field'],
                    'actual': current_value,
                    'limit': expected,
                }
                result.validaciones.append(error)
                result.errores.append(error)

    def _compare(self, left, operator, right):
        if operator == '<=':
            return left <= right
        if operator == '<':
            return left < right
        if operator == '>=':
            return left >= right
        if operator == '>':
            return left > right
        if operator == '==':
            return left == right
        if operator == '!=':
            return left != right
        return False

class SchedulingRuleExecutor:
    def __init__(self, evaluator=None):
        self.evaluator = evaluator or SafeExpressionEvaluator()

    def execute(self, rule_config: dict, context: EngineContext, result: EngineResult):
        obligation = rule_config.get('obligation', {})
        conditions = obligation.get('profile_conditions', [])

        applies = all(
            self.evaluator.evaluate(cond, {'profile': context.profile_data, 'financial': context.financial_data})
            for cond in conditions
        ) if conditions else True

        if not applies:
            return

        due_date = self._build_due_date(context.periodo, obligation.get('periodicity'), obligation.get('due_day', 1))

        result.obligaciones.append({
            'codigo': rule_config.get('codigo'),
            'nombre': obligation.get('name'),
            'periodicidad': obligation.get('periodicity'),
            'fechavencimiento': due_date,
        })

    def _build_due_date(self, periodo: str, periodicidad: str, due_day: int):
        year, month = periodo.split('-')
        month = int(month)
        year = int(year)

        if periodicidad == 'ANUAL':
            return date(year, 12, due_day)
        return date(year, month, due_day)

class ExportRuleExecutor:
    def execute(self, rule_config: dict, context: EngineContext, result: EngineResult):
        missing = []
        payload = {}

        for field in rule_config.get('required_fields', []):
            source = rule_config.get('mapping', {}).get(field)
            value = self._resolve(source, context, result)
            if value in (None, '', []):
                missing.append(field)
            payload[field] = value

        result.exportables.append({
            'codigo': rule_config.get('codigo'),
            'format': rule_config.get('format'),
            'payload': payload,
            'missing_fields': missing,
            'ready': len(missing) == 0,
        })

    def _resolve(self, source: str, context: EngineContext, result: EngineResult):
        if not source:
            return None
        if source.startswith('financial.'):
            return context.financial_data.get(source.split('.', 1)[1])
        if source.startswith('context.'):
            return getattr(context, source.split('.', 1)[1], None)
        if source.startswith('results.'):
            return result.calculos.get(source.split('.', 1)[1])
        return None

class TaxRulesEngineService:
    def __init__(self):
        self.calculation_executor = CalculationRuleExecutor()
        self.validation_executor = ValidationRuleExecutor()
        self.scheduling_executor = SchedulingRuleExecutor()
        self.export_executor = ExportRuleExecutor()

    def execute(self, context: EngineContext) -> EngineResult:
        normativa = self._get_normativa_vigente(context.pais_id)
        result = EngineResult(normativa_id=normativa.id if normativa else None)

        if not normativa:
            result.errores.append({
                'code': 'NORMATIVA_NO_VIGENTE',
                'message': 'No existe normativa vigente para el país indicado.'
            })
            return result

        configs = self._get_configs(normativa.id)

        for cfg in configs:
            payload = dict(cfg.config)
            payload['codigo'] = cfg.codigo

            if cfg.tiporegla == 'CALCULO':
                self.calculation_executor.execute(payload, context, result)
            elif cfg.tiporegla == 'VALIDACION':
                self.validation_executor.execute(payload, context, result)
            elif cfg.tiporegla == 'SCHEDULING':
                self.scheduling_executor.execute(payload, context, result)
            elif cfg.tiporegla == 'EXPORTACION':
                self.export_executor.execute(payload, context, result)

        return result

    def populate_schedule(self, usuario_id: int, perfil: PerfilTributario, periodo: str, financial_data=None):
        financial_data = financial_data or {}
        context = EngineContext(
            usuario_id=usuario_id,
            pais_id=perfil.pais_id,
            periodo=periodo,
            financial_data=financial_data,
            profile_data={
                'regimen': perfil.regimen,
                'actividad': perfil.actividad,
                **perfil.atributos
            }
        )
        result = self.execute(context)

        normativa = self._get_normativa_vigente(perfil.pais_id)
        for item in result.obligaciones:
            ObligacionTributariaProgramada.objects.get_or_create(
                usuario_id=usuario_id,
                perfil=perfil,
                normativa=normativa,
                codigoobligacion=item['codigo'],
                fechavencimiento=item['fechavencimiento'],
                defaults={
                    'nombreobligacion': item['nombre'],
                    'periodicidad': item['periodicidad'],
                    'metadata': {'periodo': periodo}
                }
            )

        return result

    def _get_normativa_vigente(self, pais_id: int):
        today = date.today()
        return (
            NormativaTributaria.objects
            .filter(
                pais_id=pais_id,
                estado='VIGENTE',
                vigentedesde__lte=today
            )
            .filter(Q(vigentehasta__isnull=True) | Q(vigentehasta__gte=today))
            .order_by('-vigentedesde', '-id')
            .first()
        )

    def _get_configs(self, normativa_id: int):
        today = date.today()
        return (
            NormativaConfig.objects
            .filter(
                normativa_id=normativa_id,
                activa=True,
                vigentedesde__lte=today
            )
            .filter(Q(vigentehasta__isnull=True) | Q(vigentehasta__gte=today))
            .order_by('tiporegla', 'prioridad', 'id')
        )