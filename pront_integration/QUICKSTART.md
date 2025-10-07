# 🚀 Quick Start - Integração Fluxi <-> Pront

Guia rápido para começar a usar a integração em **5 minutos**.

## ⚡ Passo a Passo

### 1️⃣ Gerar API Key (30 segundos)

Abra seu navegador e acesse:
```
http://localhost:81/pront/api/fluxi_api.php?action=health&api_key=test
```

Você verá algo como:
```json
{
  "success": true,
  "message": "API funcionando",
  "data": {
    "status": "online",
    "timestamp": "2025-01-07T20:00:00-03:00"
  }
}
```

**Copie a chave gerada** que está em:
```
d:\laragon-6.0.0\www\pront\api\fluxi_api_key.txt
```

### 2️⃣ Configurar Fluxi (1 minuto)

Edite ou crie o arquivo `d:\fluxi\.env` e adicione:

```env
# Integração com Pront
PRONT_API_URL=http://localhost:81/pront/api
PRONT_API_KEY=COLE_A_CHAVE_AQUI
```

### 3️⃣ Testar Conexão (1 minuto)

Abra o terminal no diretório do Fluxi:

```bash
cd d:\fluxi
python pront_integration\test_integration.py
```

Você deve ver:
```
🧪 TESTES DE INTEGRAÇÃO FLUXI <-> PRONT
✅ PASSOU - Health Check
✅ PASSOU - Buscar Paciente
✅ PASSOU - Aniversariantes
🎉 Integração funcionando perfeitamente!
```

### 4️⃣ Habilitar no Agente (2 minutos)

Edite `d:\fluxi\agente\agente_service.py`:

**No início do arquivo, adicione:**
```python
from pront_integration.pront_tools import PRONT_TOOLS, PRONT_TOOL_FUNCTIONS
```

**Na função `processar_mensagem`, localize onde as ferramentas são definidas e adicione:**
```python
# Adicionar ferramentas Pront
tools.extend(PRONT_TOOLS)
```

**No processamento de tool_calls, adicione:**
```python
elif nome_funcao in PRONT_TOOL_FUNCTIONS:
    funcao = PRONT_TOOL_FUNCTIONS[nome_funcao]
    resultado_ferramenta = await funcao(**argumentos)
```

### 5️⃣ Reiniciar Fluxi

```bash
# No terminal do Fluxi, pressione Ctrl+C e execute novamente:
python main.py
```

## ✅ Pronto!

Agora você pode enviar mensagens pelo WhatsApp como:

```
👤 Usuário: "Busque o paciente João Silva"

🤖 Bot: 
✅ 1 paciente(s) encontrado(s):

📋 Prontuário: 123
👤 Nome: João Silva  
🆔 CPF: 123.456.789-00
📞 Telefone: (11) 98765-4321
```

```
👤 Usuário: "Agende consulta para o paciente 123 amanhã às 14h com Dr. Pedro"

🤖 Bot:
✅ Consulta agendada com sucesso!
📋 ID do Agendamento: 456
👤 Paciente: 123
📅 Data: 2025-01-08
⏰ Horário: 14:00
```

## 🎯 Comandos Disponíveis

| Comando | Exemplo |
|---------|---------|
| **Buscar paciente** | "Busque o paciente com CPF 12345678900" |
| **Agendar** | "Agende consulta para paciente 123 dia 15/01 às 14h" |
| **Ver agendamentos** | "Quais são os agendamentos de hoje?" |
| **Registrar presença** | "Registre presença do paciente 123" |
| **Aniversariantes** | "Quem faz aniversário hoje?" |

## ❓ Problemas?

### Erro: "API Key inválida"
✅ Verifique se copiou a chave corretamente do arquivo `fluxi_api_key.txt`

### Erro: "Connection refused"
✅ Confirme que o Laragon está rodando (`http://localhost:81/pront`)

### Erro: "Tabela não existe"
✅ Execute as migrações do banco de dados do Pront (veja README.md do Pront)

## 📚 Documentação Completa

Leia o arquivo `README.md` para detalhes sobre:
- Todas as funcionalidades disponíveis
- API endpoints completos
- Segurança e autenticação
- Troubleshooting avançado
