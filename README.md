# GitHub Crawler para Átomos de Confusão

Um crawler que busca e analisa repositórios no GitHub em busca de "átomos de confusão" em código-fonte. Átomos de confusão são padrões de código que podem ser difíceis de entender ou que podem levar a erros de interpretação por desenvolvedores.

## Funcionalidades

- **Busca Avançada**: Filtra repositórios por linguagem, estrelas, forks e data de atualização
- **Detecção de Padrões**: Identifica padrões de código potencialmente confusos usando expressões regulares
- **Análise com IA**: Utiliza a API Google Gemini para análise profunda de código
- **Relatórios Detalhados**: Gera relatórios em formatos JSON, CSV e HTML
- **Interface CLI**: Configuração flexível via linha de comando
- **Filtros Inteligentes**: Evita falsos positivos em métodos mágicos e comentários padrão

## Requisitos

- Python 3.8+
- Token de acesso do GitHub
- Chave de API do Google Gemini

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/crawlerGithub.git
   cd crawlerGithub
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```
   GITHUB_ACCESS_TOKEN=seu_token_do_github
   GOOGLE_GEMINI_API_KEY=sua_chave_da_api_gemini
   ```

## Uso

### Comando Básico

```bash
python app.py
```

### Exemplos

```bash
# Análise com filtros específicos
python app.py --query "código confuso" --languages python java --min-stars 50 --deep-analysis

# Analisar um repositório específico
python app.py --analyze-repo "tensorflow/tensorflow" --deep-analysis

# Buscar repositórios JavaScript com muitas estrelas
python app.py --query "complex code" --languages javascript --min-stars 1000 --max-repos 3

# Gerar apenas relatórios HTML
python app.py --format html --output-dir "meus_relatorios"
```

### Parâmetros

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--query` | Termo de busca | "code confusion" |
| `--languages` | Linguagens para filtrar | python, javascript, java |
| `--min-stars` | Mínimo de estrelas | 10 |
| `--min-forks` | Mínimo de forks | 5 |
| `--max-repos` | Máximo de repositórios | 5 |
| `--max-files` | Máximo de arquivos por repo | config.MAX_FILES_PER_REPO |
| `--updated-after` | Data mínima de atualização | 2023-01-01 |
| `--analyze-repo` | Repositório específico | - |
| `--deep-analysis` | Ativar análise com Gemini | false |
| `--output-dir` | Diretório de relatórios | "reports" |
| `--format` | Formato do relatório | all (json,csv,html) |

## Estrutura do Projeto

```
├── app.py              # Ponto de entrada principal
├── github_api.py       # Interação com API do GitHub
├── gemini_api.py       # Interação com API do Google Gemini
├── report_generator.py # Gerador de relatórios
├── config.py           # Configurações e constantes
├── example.py          # Exemplos de uso
└── requirements.txt    # Dependências do projeto
```

## Linguagens Suportadas

- Python
- JavaScript
- Java

## Melhorias Recentes

- Exclusão de métodos mágicos comuns do Python da detecção
- Compatibilidade com comentários padrão de frameworks
- Relatórios HTML interativos com análises do Gemini
- Análise em duas etapas para economia de recursos

## Licença

MIT
