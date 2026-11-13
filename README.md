# MBA IA · Prompt Engineering

Projeto em Python, LangChain e LangSmith que transforma relatos de bugs em User Stories com critérios de aceitação verificáveis. O fluxo baixa o prompt público original, publica a v2 do YAML e avalia o prompt publicado nos 15 casos do curso.

## Técnicas Aplicadas (Fase 2)

- **Few-shot Learning.** Três pares de entrada e saída mostram como a resposta muda com a informação disponível. O filtro de um catálogo exemplifica uma história simples. A importação de estoque mostra critérios separados para validação e gravação. O relato “Deu erro ontem” demonstra como pedir os dados essenciais antes de propor uma história.
- **Role Prompting.** A persona de Product Manager sênior dá ao modelo a responsabilidade de traduzir o incidente em valor para o usuário e em critérios que QA consegue verificar. Na importação, por exemplo, a história expressa a necessidade de saber quais linhas foram gravadas e os critérios descrevem o que o painel deve exibir.
- **Skeleton of Thought.** A estrutura começa com persona, comportamento e benefício, seguida dos critérios no formato Dado/Quando/Então. Casos complexos ganham contexto e tarefas sugeridas. Quando a regra de negócio é incerta, a seção “A Confirmar” registra a decisão em aberto, como permitir importação parcial ou bloquear toda a planilha.

## Resultados Finais

| Aspecto | v1 | v2 |
| --- | --- | --- |
| Mensagens | O relato é interpolado no sistema e repetido na mensagem do usuário. | As regras e os exemplos ficam no sistema. A mensagem de usuário recebe o relato uma única vez. |
| Instruções | Um assistente genérico recebe o pedido de criar uma história. | A persona orienta a escolha da história e exige critérios observáveis em Markdown. |
| Escopo | A resposta fica a cargo do modelo. | A estrutura diferencia casos simples, falhas relacionadas e relatos insuficientes. A v2 pede que o modelo preserve fatos e sinalize hipóteses e dados a confirmar. |
| Exemplos | Ausentes. | Três pares próprios, fora do dataset de avaliação. |

A validação local cobre os seis requisitos estruturais com pytest. As notas das cinco métricas, o link público, as capturas do dashboard e os três traces dependem de um experimento executado com as credenciais do workspace. A avaliação oficial busca a v2 no Hub. A comparação acima descreve as diferenças de conteúdo entre as duas versões.

## Como Executar

### 1. Ambiente e credenciais

Use Python 3.10 ou superior, Git, uma conta LangSmith e acesso à API da OpenAI ou do Google. O ambiente local foi validado com Python 3.13. Execute os comandos na raiz do fork.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

No Linux ou macOS, ative com `source venv/bin/activate` e copie com `cp .env.example .env`. Se o PowerShell impedir a ativação, rode os comandos Python usando `.\venv\Scripts\python.exe`.

- Configure `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` e `USERNAME_LANGSMITH_HUB`. O handle é a parte anterior a `/nome_do_prompt` no endereço público. Se precisar criá-lo, abra um prompt no LangSmith, use **Make Public** e escolha o handle definitivo. [LangSmith Prompts](https://smith.langchain.com/prompts)
- Configure `LLM_PROVIDER=openai` com `OPENAI_API_KEY` ou `LLM_PROVIDER=google` com `GOOGLE_API_KEY`. Preencha `LLM_MODEL` e `EVAL_MODEL` com modelos disponíveis na sua conta e que aceitem `temperature=0`, usado pelo avaliador do curso. Para OpenAI, `gpt-4.1-mini` na geração e `gpt-4.1` no julgamento são uma configuração inicial enquanto estiverem disponíveis. [Modelos OpenAI](https://developers.openai.com/api/docs/models) · [Descontinuações OpenAI](https://developers.openai.com/api/docs/deprecations) · [Modelos Gemini](https://ai.google.dev/gemini-api/docs/models)
- Mantenha `LANGSMITH_TRACING=true` para registrar as chamadas. O Git ignora o arquivo `.env`.

### 2. Baixar, validar, publicar e avaliar

```sh
python src/pull_prompts.py
python -m pytest tests/test_prompts.py
python src/push_prompts.py
python src/evaluate.py
```

1. O pull grava a v1 em `prompts/bug_to_user_story_v1.yml`. A v2 está em `prompts/bug_to_user_story_v2.yml`.
2. O push cria ou atualiza `<handle>/bug_to_user_story_v2`, confirma a visibilidade pública e imprime o endereço do commit do prompt. Abra o endereço para conferir o conteúdo no Hub.
3. O avaliador cria ou reutiliza `<LANGSMITH_PROJECT>-eval` no LangSmith e registra cinco notas por exemplo. A aprovação exige que cada métrica e a média geral atinjam 0,8. Em cada iteração, abra os exemplos com nota baixa, leia os comentários dos juízes, ajuste o YAML e repita o push e a avaliação. Mantenha os mesmos modelos para comparar versões.
4. Para compartilhar o dataset com os experimentos, rode uma vez e guarde o endereço retornado.

```sh
python -c "import os; from dotenv import load_dotenv; from langsmith import Client; load_dotenv(); print(Client().share_dataset(dataset_name=os.environ['LANGSMITH_PROJECT'] + '-eval')['url'])"
```

No dashboard, capture a lista dos 15 exemplos, o resumo com as cinco notas e o tracing detalhado de pelo menos três casos. Um caso simples, um médio e um complexo mostram a variação de formato da v2.
