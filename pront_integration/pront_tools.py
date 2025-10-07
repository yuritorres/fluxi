"""
Ferramentas (Tools) para integração Pront no agente WhatsApp
Estas ferramentas são expostas para o LLM usar via function calling
"""
from typing import Dict, Any, Optional
from pront_integration.pront_client import ProntClient
import os


# Instância global do cliente
_pront_client = None

def get_pront_client() -> ProntClient:
    """Obtém ou cria instância do cliente Pront."""
    global _pront_client
    if _pront_client is None:
        _pront_client = ProntClient()
    return _pront_client


# =============================================================================
# DEFINIÇÕES DAS FERRAMENTAS PARA O LLM
# =============================================================================

PRONT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_paciente_pront",
            "description": "Busca informações de um paciente no sistema Pront por CPF, nome ou número do prontuário",
            "parameters": {
                "type": "object",
                "properties": {
                    "cpf": {
                        "type": "string",
                        "description": "CPF do paciente (com ou sem formatação)"
                    },
                    "nome": {
                        "type": "string",
                        "description": "Nome do paciente (busca parcial)"
                    },
                    "numero": {
                        "type": "integer",
                        "description": "Número do prontuário"
                    }
                },
                "required": []  # Pelo menos um dos três é necessário
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "agendar_consulta_pront",
            "description": "Agenda uma consulta ou atendimento para um paciente no sistema Pront",
            "parameters": {
                "type": "object",
                "properties": {
                    "paciente_numero": {
                        "type": "integer",
                        "description": "Número do prontuário do paciente"
                    },
                    "data": {
                        "type": "string",
                        "description": "Data do agendamento no formato YYYY-MM-DD (ex: 2025-01-15)"
                    },
                    "horario": {
                        "type": "string",
                        "description": "Horário no formato HH:MM (ex: 14:30)"
                    },
                    "profissional": {
                        "type": "string",
                        "description": "Nome do profissional que fará o atendimento (opcional)"
                    },
                    "observacao": {
                        "type": "string",
                        "description": "Observações sobre o agendamento (opcional)"
                    }
                },
                "required": ["paciente_numero", "data", "horario"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_agendamentos_pront",
            "description": "Consulta agendamentos do sistema Pront. Pode filtrar por paciente, data ou status",
            "parameters": {
                "type": "object",
                "properties": {
                    "paciente_numero": {
                        "type": "integer",
                        "description": "Número do prontuário para filtrar (opcional)"
                    },
                    "data": {
                        "type": "string",
                        "description": "Data para filtrar no formato YYYY-MM-DD (opcional)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["agendado", "confirmado", "realizado", "cancelado"],
                        "description": "Status dos agendamentos para filtrar (opcional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_presenca_pront",
            "description": "Registra a presença de um paciente em um atendimento no sistema Pront",
            "parameters": {
                "type": "object",
                "properties": {
                    "paciente_numero": {
                        "type": "integer",
                        "description": "Número do prontuário do paciente"
                    },
                    "data": {
                        "type": "string",
                        "description": "Data do atendimento no formato YYYY-MM-DD"
                    },
                    "horario": {
                        "type": "string",
                        "description": "Horário no formato HH:MM (opcional, usa horário atual se não fornecido)"
                    },
                    "tipo_atendimento": {
                        "type": "string",
                        "enum": ["PRESENCIAL", "ONLINE", "TELEMEDICINA"],
                        "description": "Tipo de atendimento (opcional, padrão: PRESENCIAL)"
                    },
                    "observacao": {
                        "type": "string",
                        "description": "Observações sobre o atendimento (opcional)"
                    }
                },
                "required": ["paciente_numero", "data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_aniversariantes_pront",
            "description": "Lista aniversariantes do mês no sistema Pront. Útil para enviar mensagens de parabéns",
            "parameters": {
                "type": "object",
                "properties": {
                    "mes": {
                        "type": "integer",
                        "description": "Mês para consultar (1-12). Se não fornecido, usa mês atual",
                        "minimum": 1,
                        "maximum": 12
                    },
                    "dia": {
                        "type": "integer",
                        "description": "Dia específico do mês (1-31) (opcional)",
                        "minimum": 1,
                        "maximum": 31
                    }
                },
                "required": []
            }
        }
    }
]


# =============================================================================
# IMPLEMENTAÇÕES DAS FERRAMENTAS
# =============================================================================

async def buscar_paciente_pront(
    cpf: Optional[str] = None,
    nome: Optional[str] = None,
    numero: Optional[int] = None
) -> str:
    """Busca paciente no sistema Pront."""
    try:
        client = get_pront_client()
        resultado = await client.buscar_paciente(cpf=cpf, nome=nome, numero=numero)
        
        if not resultado.get('success'):
            return f"❌ Erro: {resultado.get('error', 'Erro desconhecido')}"
        
        pacientes = resultado.get('data', [])
        
        if not pacientes:
            return "❌ Nenhum paciente encontrado com esses critérios."
        
        # Formatar resposta
        resposta = f"✅ {len(pacientes)} paciente(s) encontrado(s):\n\n"
        
        for p in pacientes[:5]:  # Limitar a 5 resultados
            resposta += f"📋 **Prontuário:** {p['numero']}\n"
            resposta += f"👤 **Nome:** {p['nome']}\n"
            
            if p.get('cpf'):
                resposta += f"🆔 **CPF:** {p['cpf']}\n"
            if p.get('data_nascimento'):
                resposta += f"🎂 **Data Nasc:** {p['data_nascimento']}\n"
            if p.get('telefone'):
                resposta += f"📞 **Telefone:** {p['telefone']}\n"
            
            # Responsáveis
            if p.get('responsaveis'):
                resposta += f"👨‍👩‍👧 **Responsáveis:**\n"
                for resp in p['responsaveis']:
                    resposta += f"   - {resp['nome']}"
                    if resp.get('cpf'):
                        resposta += f" (CPF: {resp['cpf']})"
                    resposta += "\n"
            
            resposta += "\n---\n\n"
        
        return resposta.strip()
        
    except Exception as e:
        return f"❌ Erro ao buscar paciente: {str(e)}"


async def agendar_consulta_pront(
    paciente_numero: int,
    data: str,
    horario: str,
    profissional: Optional[str] = None,
    observacao: Optional[str] = None
) -> str:
    """Agenda consulta no sistema Pront."""
    try:
        client = get_pront_client()
        
        # Garantir formato HH:MM:SS
        if len(horario) == 5:  # HH:MM
            horario += ":00"
        
        resultado = await client.agendar_consulta(
            paciente_numero=paciente_numero,
            data=data,
            horario=horario,
            profissional=profissional,
            observacao=observacao
        )
        
        if not resultado.get('success'):
            return f"❌ Erro ao agendar: {resultado.get('error', 'Erro desconhecido')}"
        
        agendamento_id = resultado.get('data', {}).get('id')
        
        resposta = "✅ **Consulta agendada com sucesso!**\n\n"
        resposta += f"📋 **ID do Agendamento:** {agendamento_id}\n"
        resposta += f"👤 **Paciente (Prontuário):** {paciente_numero}\n"
        resposta += f"📅 **Data:** {data}\n"
        resposta += f"⏰ **Horário:** {horario[:5]}\n"
        
        if profissional:
            resposta += f"👨‍⚕️ **Profissional:** {profissional}\n"
        if observacao:
            resposta += f"📝 **Observação:** {observacao}\n"
        
        return resposta
        
    except Exception as e:
        return f"❌ Erro ao agendar consulta: {str(e)}"


async def consultar_agendamentos_pront(
    paciente_numero: Optional[int] = None,
    data: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """Consulta agendamentos no sistema Pront."""
    try:
        client = get_pront_client()
        resultado = await client.listar_agendamentos(
            paciente_numero=paciente_numero,
            data=data,
            status=status
        )
        
        if not resultado.get('success'):
            return f"❌ Erro: {resultado.get('error', 'Erro desconhecido')}"
        
        agendamentos = resultado.get('data', [])
        
        if not agendamentos:
            return "📅 Nenhum agendamento encontrado com esses filtros."
        
        resposta = f"📅 **{len(agendamentos)} agendamento(s) encontrado(s):**\n\n"
        
        for ag in agendamentos[:10]:  # Limitar a 10
            resposta += f"🆔 **ID:** {ag['id']}\n"
            resposta += f"👤 **Paciente:** {ag['paciente_nome']} (Nº {ag['paciente_numero']})\n"
            resposta += f"📅 **Data:** {ag['data']}\n"
            resposta += f"⏰ **Horário:** {ag['horario']}\n"
            resposta += f"📊 **Status:** {ag['status']}\n"
            
            if ag.get('profissional'):
                resposta += f"👨‍⚕️ **Profissional:** {ag['profissional']}\n"
            if ag.get('observacao'):
                resposta += f"📝 **Obs:** {ag['observacao']}\n"
            
            resposta += "\n---\n\n"
        
        return resposta.strip()
        
    except Exception as e:
        return f"❌ Erro ao consultar agendamentos: {str(e)}"


async def registrar_presenca_pront(
    paciente_numero: int,
    data: str,
    horario: Optional[str] = None,
    tipo_atendimento: str = "PRESENCIAL",
    observacao: Optional[str] = None
) -> str:
    """Registra presença no sistema Pront."""
    try:
        client = get_pront_client()
        
        if horario and len(horario) == 5:
            horario += ":00"
        
        resultado = await client.registrar_presenca(
            paciente_numero=paciente_numero,
            data=data,
            horario=horario,
            tipo_atendimento=tipo_atendimento,
            observacao=observacao
        )
        
        if not resultado.get('success'):
            return f"❌ Erro ao registrar presença: {resultado.get('error', 'Erro desconhecido')}"
        
        presenca_id = resultado.get('data', {}).get('id')
        
        resposta = "✅ **Presença registrada com sucesso!**\n\n"
        resposta += f"🆔 **ID da Presença:** {presenca_id}\n"
        resposta += f"👤 **Paciente (Prontuário):** {paciente_numero}\n"
        resposta += f"📅 **Data:** {data}\n"
        resposta += f"⏰ **Horário:** {horario or 'Horário atual'}\n"
        resposta += f"📍 **Tipo:** {tipo_atendimento}\n"
        
        if observacao:
            resposta += f"📝 **Observação:** {observacao}\n"
        
        return resposta
        
    except Exception as e:
        return f"❌ Erro ao registrar presença: {str(e)}"


async def listar_aniversariantes_pront(
    mes: Optional[int] = None,
    dia: Optional[int] = None
) -> str:
    """Lista aniversariantes do sistema Pront."""
    try:
        client = get_pront_client()
        resultado = await client.listar_aniversariantes(mes=mes, dia=dia)
        
        if not resultado.get('success'):
            return f"❌ Erro: {resultado.get('error', 'Erro desconhecido')}"
        
        aniversariantes = resultado.get('data', [])
        
        if not aniversariantes:
            filtro = f" do dia {dia}" if dia else ""
            mes_nome = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                       "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            mes_texto = mes_nome[mes] if mes else "atual"
            return f"🎂 Nenhum aniversariante encontrado em {mes_texto}{filtro}."
        
        resposta = f"🎂 **{len(aniversariantes)} aniversariante(s):**\n\n"
        
        for aniv in aniversariantes[:20]:  # Limitar a 20
            resposta += f"👤 **{aniv['nome']}** (Nº {aniv['numero']})\n"
            resposta += f"🎂 **Aniversário:** {aniv['data_nascimento']}\n"
            resposta += f"🎈 **Idade:** {aniv['idade']} anos\n"
            
            if aniv.get('telefone'):
                resposta += f"📞 **Telefone:** {aniv['telefone']}\n"
            
            resposta += "\n---\n\n"
        
        return resposta.strip()
        
    except Exception as e:
        return f"❌ Erro ao listar aniversariantes: {str(e)}"


# =============================================================================
# MAPEAMENTO DE FUNÇÕES
# =============================================================================

PRONT_TOOL_FUNCTIONS = {
    "buscar_paciente_pront": buscar_paciente_pront,
    "agendar_consulta_pront": agendar_consulta_pront,
    "consultar_agendamentos_pront": consultar_agendamentos_pront,
    "registrar_presenca_pront": registrar_presenca_pront,
    "listar_aniversariantes_pront": listar_aniversariantes_pront
}
