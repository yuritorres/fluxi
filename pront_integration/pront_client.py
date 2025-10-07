"""
Cliente HTTP para consumir API do sistema Pront
"""
import httpx
from typing import Optional, Dict, List, Any
from datetime import date, datetime
import os


class ProntClient:
    """Cliente para integração com API do sistema Pront."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Inicializa o cliente Pront.
        
        Args:
            base_url: URL base da API Pront (ex: http://localhost/pront/api)
            api_key: Chave de API para autenticação
        """
        self.base_url = base_url or os.getenv("PRONT_API_URL", "http://localhost:81/pront/api")
        self.api_key = api_key or os.getenv("PRONT_API_KEY")
        
        if not self.api_key:
            raise ValueError("PRONT_API_KEY não configurada. Defina via .env ou parâmetro")
        
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica se a API está online."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/fluxi_api.php?action=health",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def buscar_paciente(
        self, 
        cpf: Optional[str] = None,
        nome: Optional[str] = None,
        numero: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Busca paciente por CPF, nome ou número.
        
        Args:
            cpf: CPF do paciente (apenas números)
            nome: Nome do paciente (busca parcial)
            numero: Número do prontuário
            
        Returns:
            Dados do paciente incluindo responsáveis
        """
        if not any([cpf, nome, numero]):
            raise ValueError("Informe pelo menos um parâmetro: cpf, nome ou numero")
        
        params = {}
        if cpf:
            params['cpf'] = cpf.replace('.', '').replace('-', '')
        if nome:
            params['nome'] = nome
        if numero:
            params['numero'] = str(numero)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/fluxi_api.php",
                params={'action': 'paciente', **params},
                headers=self.headers,
                timeout=15.0
            )
            return response.json()
    
    async def cadastrar_paciente(self, dados_paciente: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cadastra novo paciente no sistema.
        
        Args:
            dados_paciente: Dicionário com dados do paciente
                - nome (obrigatório)
                - empresa_id (obrigatório)
                - cpf, telefone, data_nascimento, etc (opcionais)
                - responsaveis: lista de {nome, cpf}
        
        Returns:
            Dados do paciente criado incluindo número gerado
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/fluxi_api.php?action=paciente",
                headers=self.headers,
                json=dados_paciente,
                timeout=15.0
            )
            return response.json()
    
    async def atualizar_paciente(
        self, 
        numero: int, 
        dados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza dados de um paciente existente.
        
        Args:
            numero: Número do prontuário
            dados: Campos a atualizar
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/fluxi_api.php",
                params={'action': 'paciente', 'numero': str(numero)},
                headers=self.headers,
                json=dados,
                timeout=15.0
            )
            return response.json()
    
    async def agendar_consulta(
        self,
        paciente_numero: int,
        data: str,  # YYYY-MM-DD
        horario: str,  # HH:MM:SS
        profissional: Optional[str] = None,
        observacao: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Agenda uma consulta/atendimento para o paciente.
        
        Args:
            paciente_numero: Número do prontuário
            data: Data do agendamento (formato YYYY-MM-DD)
            horario: Horário (formato HH:MM:SS ou HH:MM)
            profissional: Nome do profissional
            observacao: Observações sobre o agendamento
        """
        dados = {
            'paciente_numero': paciente_numero,
            'data': data,
            'horario': horario,
            'profissional': profissional,
            'observacao': observacao,
            'status': 'agendado'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/fluxi_api.php?action=agendar",
                headers=self.headers,
                json=dados,
                timeout=15.0
            )
            return response.json()
    
    async def listar_agendamentos(
        self,
        paciente_numero: Optional[int] = None,
        data: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lista agendamentos com filtros opcionais.
        
        Args:
            paciente_numero: Filtrar por paciente
            data: Filtrar por data (YYYY-MM-DD)
            status: Filtrar por status (agendado, confirmado, realizado, cancelado)
        """
        params = {'action': 'agendamentos'}
        if paciente_numero:
            params['paciente_numero'] = str(paciente_numero)
        if data:
            params['data'] = data
        if status:
            params['status'] = status
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/fluxi_api.php",
                params=params,
                headers=self.headers,
                timeout=15.0
            )
            return response.json()
    
    async def registrar_presenca(
        self,
        paciente_numero: int,
        data: str,
        horario: Optional[str] = None,
        tipo_atendimento: str = "PRESENCIAL",
        observacao: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra presença do paciente em atendimento.
        
        Args:
            paciente_numero: Número do prontuário
            data: Data do atendimento (YYYY-MM-DD)
            horario: Horário (HH:MM:SS). Se None, usa horário atual
            tipo_atendimento: Tipo (PRESENCIAL, ONLINE, etc)
            observacao: Observações
        """
        dados = {
            'paciente_numero': paciente_numero,
            'data': data,
            'horario': horario or datetime.now().strftime('%H:%M:%S'),
            'tipo_atendimento': tipo_atendimento,
            'observacao': observacao
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/fluxi_api.php?action=registrar_presenca",
                headers=self.headers,
                json=dados,
                timeout=15.0
            )
            return response.json()
    
    async def listar_aniversariantes(
        self,
        mes: Optional[int] = None,
        dia: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Lista aniversariantes do mês.
        
        Args:
            mes: Mês (1-12). Se None, usa mês atual
            dia: Dia específico (opcional)
        """
        params = {'action': 'aniversariantes'}
        if mes:
            params['mes'] = str(mes)
        if dia:
            params['dia'] = str(dia)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/fluxi_api.php",
                params=params,
                headers=self.headers,
                timeout=15.0
            )
            return response.json()
