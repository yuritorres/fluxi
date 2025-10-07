# 🔧 Modificações Necessárias no Agente

Para habilitar as ferramentas Pront no agente WhatsApp, siga estes passos:

## 1. Editar `agente_service.py`

### Adicionar imports no início do arquivo:

```python
# ADICIONAR ESTAS LINHAS após os outros imports:
from pront_integration.pront_tools import PRONT_TOOLS, PRONT_TOOL_FUNCTIONS
```

### Adicionar ferramentas no método `processar_mensagem`

Localize onde as ferramentas são definidas (aproximadamente linha 380-415) e adicione:

```python
# Após adicionar as ferramentas padrão (buscar_base_conhecimento, etc):

# ADICIONAR FERRAMENTAS PRONT
tools.extend(PRONT_TOOLS)
print(f"📦 [AGENTE] {len(PRONT_TOOLS)} ferramentas Pront adicionadas")
```

### Processar chamadas das ferramentas Pront

Localize o loop de processamento de `tool_calls` (aproximadamente linha 450-520) e adicione:

```python
# Após o processamento das outras ferramentas, adicione este elif:

elif nome_funcao in PRONT_TOOL_FUNCTIONS:
    print(f"🏥 [PRONT] Executando: {nome_funcao}")
    funcao = PRONT_TOOL_FUNCTIONS[nome_funcao]
    try:
        resultado_ferramenta = await funcao(**argumentos)
        print(f"✅ [PRONT] Resultado: {resultado_ferramenta[:100]}...")
    except Exception as e:
        resultado_ferramenta = f"❌ Erro ao executar {nome_funcao}: {str(e)}"
        print(f"❌ [PRONT] Erro: {str(e)}")
    
    ferramentas_usadas.append({
        "nome": nome_funcao,
        "argumentos": argumentos,
        "resultado": resultado_ferramenta
    })
```

## 2. Código Completo de Exemplo

### Localização: Aproximadamente linha 380-415

```python
# Definir ferramentas disponíveis
tools = []

# Verificar se há RAG ativo
if agente.rag_ativo_id:
    rag = RAGService.obter_por_id(db, agente.rag_ativo_id)
    if rag and rag.ativo:
        # ... código existente de RAG ...
        tools.append({
            "type": "function",
            "function": {
                "name": "buscar_base_conhecimento",
                # ... resto da definição ...
            }
        })

# ADICIONAR AQUI - Ferramentas Pront:
tools.extend(PRONT_TOOLS)
print(f"📦 [AGENTE] Total de {len(tools)} ferramentas disponíveis")
```

### Localização: Aproximadamente linha 450-520

```python
# Processar tool_calls
if tool_calls:
    print(f"🔧 [AGENTE] {len(tool_calls)} ferramenta(s) solicitada(s)")
    
    for tool_call in tool_calls:
        nome_funcao = tool_call.function.name
        argumentos_str = tool_call.function.arguments
        argumentos = json.loads(argumentos_str)
        
        print(f"🔧 [AGENTE] Chamando: {nome_funcao} com {argumentos}")
        
        if nome_funcao == "buscar_base_conhecimento":
            # ... código existente de RAG ...
            pass
        
        # ADICIONAR AQUI - Ferramentas Pront:
        elif nome_funcao in PRONT_TOOL_FUNCTIONS:
            print(f"🏥 [PRONT] Executando: {nome_funcao}")
            funcao = PRONT_TOOL_FUNCTIONS[nome_funcao]
            try:
                resultado_ferramenta = await funcao(**argumentos)
                print(f"✅ [PRONT] Sucesso")
            except Exception as e:
                resultado_ferramenta = f"❌ Erro: {str(e)}"
                print(f"❌ [PRONT] Erro: {str(e)}")
            
            ferramentas_usadas.append({
                "nome": nome_funcao,
                "argumentos": argumentos,
                "resultado": resultado_ferramenta
            })
        
        else:
            print(f"⚠️ [AGENTE] Ferramenta desconhecida: {nome_funcao}")
            resultado_ferramenta = f"Ferramenta {nome_funcao} não está disponível"
```

## 3. Alternativa: Aplicar Patch Automático

Crie o arquivo `d:\fluxi\apply_pront_integration.py`:

```python
"""
Script para aplicar automaticamente a integração Pront ao agente
Execute: python apply_pront_integration.py
"""

import re

def apply_patch():
    file_path = "agente/agente_service.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Adicionar import
    if 'from pront_integration.pront_tools import' not in content:
        import_pos = content.find('from llm_providers.llm_integration_service import')
        if import_pos != -1:
            line_end = content.find('\n', import_pos)
            content = (content[:line_end+1] + 
                      'from pront_integration.pront_tools import PRONT_TOOLS, PRONT_TOOL_FUNCTIONS\n' +
                      content[line_end+1:])
            print("✅ Import adicionado")
    
    # 2. Adicionar ferramentas ao tools array
    if 'tools.extend(PRONT_TOOLS)' not in content:
        # Localizar onde adicionar (após definição de buscar_base_conhecimento)
        pattern = r'(\}\s*\]\s*\}\s*\)\s*\n\s*# Variáveis de controle)'
        match = re.search(pattern, content)
        if match:
            pos = match.start(1)
            content = (content[:pos] + 
                      '\n    # Adicionar ferramentas Pront\n' +
                      '    tools.extend(PRONT_TOOLS)\n' +
                      content[pos:])
            print("✅ Ferramentas Pront adicionadas ao array")
    
    # 3. Adicionar processamento de tool_calls
    if 'elif nome_funcao in PRONT_TOOL_FUNCTIONS:' not in content:
        # Encontrar o local certo no processamento de tool_calls
        pattern = r'(ferramentas_usadas\.append\(\{[^}]+\}\))\s*(# Adicionar mensagem)'
        match = re.search(pattern, content)
        if match:
            pos = match.end(1)
            patch = '''
                
                elif nome_funcao in PRONT_TOOL_FUNCTIONS:
                    print(f"🏥 [PRONT] Executando: {nome_funcao}")
                    funcao = PRONT_TOOL_FUNCTIONS[nome_funcao]
                    try:
                        resultado_ferramenta = await funcao(**argumentos)
                        print(f"✅ [PRONT] Sucesso")
                    except Exception as e:
                        resultado_ferramenta = f"❌ Erro: {str(e)}"
                        print(f"❌ [PRONT] Erro: {str(e)}")
                    
                    ferramentas_usadas.append({
                        "nome": nome_funcao,
                        "argumentos": argumentos,
                        "resultado": resultado_ferramenta
                    })
'''
            content = content[:pos] + patch + content[pos:]
            print("✅ Processamento de tool_calls adicionado")
    
    # Salvar backup
    with open(file_path + '.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    print("💾 Backup criado: agente/agente_service.py.backup")
    
    # Salvar arquivo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Arquivo atualizado: agente/agente_service.py")
    
    print("\n🎉 Integração Pront aplicada com sucesso!")
    print("⚠️  Reinicie o servidor Fluxi para aplicar as mudanças")

if __name__ == "__main__":
    try:
        apply_patch()
    except Exception as e:
        print(f"❌ Erro ao aplicar patch: {e}")
        print("💡 Aplique as modificações manualmente seguindo INTEGRATION_STEPS.md")
```

Salve o arquivo como `d:\fluxi\apply_pront_integration.py` e execute:
```bash
python apply_pront_integration.py
```

## 4. Verificar Integração

Após aplicar as modificações:

1. **Reinicie o Fluxi**:
   ```bash
   python main.py
   ```

2. **Verifique os logs de inicialização**:
   ```
   📦 [AGENTE] Total de X ferramentas disponíveis
   ```

3. **Envie mensagem de teste via WhatsApp**:
   ```
   "Busque o paciente com CPF 12345678900"
   ```

4. **Observe os logs**:
   ```
   🏥 [PRONT] Executando: buscar_paciente_pront
   ✅ [PRONT] Sucesso
   ```

## 5. Troubleshooting

### Erro: "Module not found: pront_integration"
- Certifique-se de que a pasta `pront_integration` está em `d:\fluxi\`
- Verifique se o `__init__.py` existe na pasta

### Erro: "PRONT_API_KEY não configurada"
- Configure as variáveis de ambiente no `.env`
- Verifique se está carregando o arquivo `.env` (use python-dotenv)

### Ferramentas não aparecem no LLM
- Verifique se `tools.extend(PRONT_TOOLS)` está sendo executado
- Adicione `print(f"Tools: {[t['function']['name'] for t in tools]}")` para debug

## ✅ Pronto!

Após seguir estes passos, o agente WhatsApp terá acesso completo ao sistema Pront via API.
