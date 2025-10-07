# 🏥 Integração Fluxi <-> Pront

Integração completa entre o sistema **Fluxi** (WhatsApp Bot) e o **Pront** (Sistema de Prontuários Médicos).

## 📋 Funcionalidades

### ✅ Implementadas

- **Buscar Paciente**: Por CPF, nome ou número do prontuário
- **Agendar Consultas**: Via WhatsApp com confirmação automática
- **Consultar Agendamentos**: Verificar agenda de pacientes
- **Registrar Presenças**: Confirmação de comparecimento
- **Aniversariantes**: Lista automática para enviar mensagens de parabéns

## 🚀 Instalação e Configuração

### 1. Configurar API no Pront

A API REST já foi criada em: `d:\laragon-6.0.0\www\pront\api\fluxi_api.php`

**Gerar API Key:**

```bash
# Acessar via navegador para gerar a chave automaticamente:
http://localhost:81/pront/api/fluxi_api.php?action=health&api_key=test
```

A primeira execução criará o arquivo `fluxi_api_key.txt` com uma chave aleatória segura. **Copie essa chave!**

### 2. Configurar Fluxi

Adicione as variáveis de ambiente no arquivo `.env` do Fluxi:

```env
# Integração com Pront
PRONT_API_URL=http://localhost:81/pront/api
PRONT_API_KEY=sua_chave_aqui_gerada_no_passo_1
```

### 3. Instalar Dependências

```bash
cd d:\fluxi
pip install httpx
```

### 4. Habilitar Ferramentas no Agente

Edite `d:\fluxi\agente\agente_service.py` e adicione:

```python
# No topo do arquivo, adicione:
from pront_integration.pront_tools import PRONT_TOOLS, PRONT_TOOL_FUNCTIONS

# Na função processar_mensagem, adicione as ferramentas Pront:
if agente.ativo:
    # Ferramentas padrão...
    tools.extend(ferramentas_disponiveis)
    
    # ADICIONAR AQUI:
    tools.extend(PRONT_TOOLS)
```

E no processamento de tool_calls:

```python
# Após a execução das ferramentas normais, adicione:
elif nome_funcao in PRONT_TOOL_FUNCTIONS:
    funcao = PRONT_TOOL_FUNCTIONS[nome_funcao]
    resultado_ferramenta = await funcao(**argumentos)
```

## 📝 Exemplos de Uso via WhatsApp

### Buscar Paciente

**Usuário:**
```
Olá, preciso consultar os dados do paciente João Silva
```

**Bot:**
```
✅ 1 paciente(s) encontrado(s):

📋 Prontuário: 123
👤 Nome: João Silva
🆔 CPF: 123.456.789-00
🎂 Data Nasc: 1990-05-15
📞 Telefone: (11) 98765-4321
👨‍👩‍👧 Responsáveis:
   - Maria Silva (CPF: 987.654.321-00)
```

### Agendar Consulta

**Usuário:**
```
Quero agendar consulta para o paciente 123 no dia 15/01/2025 às 14:30 com Dr. Pedro
```

**Bot:**
```
✅ Consulta agendada com sucesso!

📋 ID do Agendamento: 456
👤 Paciente (Prontuário): 123
📅 Data: 2025-01-15
⏰ Horário: 14:30
👨‍⚕️ Profissional: Dr. Pedro
```

### Verificar Agendamentos

**Usuário:**
```
Quais são os agendamentos de hoje?
```

**Bot:**
```
📅 3 agendamento(s) encontrado(s):

🆔 ID: 456
👤 Paciente: João Silva (Nº 123)
📅 Data: 2025-01-15
⏰ Horário: 14:30:00
📊 Status: agendado
👨‍⚕️ Profissional: Dr. Pedro
```

### Aniversariantes do Dia

**Usuário:**
```
Quem são os aniversariantes de hoje?
```

**Bot:**
```
🎂 2 aniversariante(s):

👤 Ana Costa (Nº 45)
🎂 Aniversário: 1985-01-15
🎈 Idade: 40 anos
📞 Telefone: (11) 91234-5678
```

## 🔧 API Endpoints

### Health Check
```http
GET /api/fluxi_api.php?action=health
X-API-Key: sua_chave
```

### Buscar Paciente
```http
GET /api/fluxi_api.php?action=paciente&cpf=12345678900
X-API-Key: sua_chave
```

### Cadastrar Paciente
```http
POST /api/fluxi_api.php?action=paciente
X-API-Key: sua_chave
Content-Type: application/json

{
  "nome": "João Silva",
  "empresa_id": 1,
  "cpf": "12345678900",
  "telefone": "(11) 98765-4321",
  "data_nascimento": "1990-05-15",
  "responsaveis": [
    {
      "nome": "Maria Silva",
      "cpf": "98765432100"
    }
  ]
}
```

### Agendar Consulta
```http
POST /api/fluxi_api.php?action=agendar
X-API-Key: sua_chave
Content-Type: application/json

{
  "paciente_numero": 123,
  "data": "2025-01-15",
  "horario": "14:30:00",
  "profissional": "Dr. Pedro",
  "observacao": "Consulta de rotina"
}
```

### Listar Agendamentos
```http
GET /api/fluxi_api.php?action=agendamentos&data=2025-01-15
X-API-Key: sua_chave
```

### Registrar Presença
```http
POST /api/fluxi_api.php?action=registrar_presenca
X-API-Key: sua_chave
Content-Type: application/json

{
  "paciente_numero": 123,
  "data": "2025-01-15",
  "horario": "14:30:00",
  "tipo_atendimento": "PRESENCIAL"
}
```

### Aniversariantes
```http
GET /api/fluxi_api.php?action=aniversariantes&mes=1&dia=15
X-API-Key: sua_chave
```

## 🔒 Segurança

- ✅ Autenticação via API Key no header `X-API-Key`
- ✅ CORS habilitado para domínios específicos
- ✅ Validação de entrada em todos os endpoints
- ✅ Proteção contra SQL Injection via PDO prepared statements
- ✅ Rate limiting recomendado (implementar no servidor web)

## 🧪 Testes

### Teste Manual via curl

```bash
# Health check
curl -H "X-API-Key: SUA_CHAVE" \
  "http://localhost:81/pront/api/fluxi_api.php?action=health"

# Buscar paciente
curl -H "X-API-Key: SUA_CHAVE" \
  "http://localhost:81/pront/api/fluxi_api.php?action=paciente&nome=João"

# Agendar consulta
curl -X POST \
  -H "X-API-Key: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{"paciente_numero":123,"data":"2025-01-15","horario":"14:30"}' \
  "http://localhost:81/pront/api/fluxi_api.php?action=agendar"
```

### Teste via Python

```python
from pront_integration.pront_client import ProntClient
import asyncio

async def test():
    client = ProntClient(
        base_url="http://localhost:81/pront/api",
        api_key="sua_chave_aqui"
    )
    
    # Health check
    result = await client.health_check()
    print(result)
    
    # Buscar paciente
    result = await client.buscar_paciente(nome="João")
    print(result)

asyncio.run(test())
```

## 📊 Monitoramento

### Logs da API

Os logs são armazenados automaticamente pelo servidor PHP. Verifique:
- Logs do Apache/Nginx
- Logs de erro do PHP (`php_error.log`)

### Métricas Recomendadas

- Taxa de sucesso das requisições
- Tempo médio de resposta
- Endpoints mais utilizados
- Erros mais comuns

## 🐛 Troubleshooting

### Erro: "API Key inválida"
- Verifique se copiou a chave correta de `fluxi_api_key.txt`
- Confirme que está enviando no header `X-API-Key`

### Erro: "Tabela não existe"
- Execute as migrações do banco de dados do Pront
- Verifique se o banco está acessível

### Erro de conexão
- Confirme que o Laragon está rodando
- Teste o acesso direto: `http://localhost:81/pront/api/fluxi_api.php?action=health&api_key=test`

## 📚 Estrutura de Arquivos

```
d:\fluxi\pront_integration\
├── __init__.py              # Módulo Python
├── pront_client.py          # Cliente HTTP para API
├── pront_tools.py           # Ferramentas para o LLM
└── README.md                # Esta documentação

d:\laragon-6.0.0\www\pront\api\
├── fluxi_api.php            # API REST completa
└── fluxi_api_key.txt        # Chave de API (gerada automaticamente)
```

## 🎯 Próximos Passos

- [ ] Implementar webhook para notificações automáticas
- [ ] Adicionar lembretes de consulta via WhatsApp
- [ ] Relatórios de atendimento via WhatsApp
- [ ] Integração com calendário (Google Calendar)
- [ ] Upload de documentos/exames via WhatsApp

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação do Pront e Fluxi.
