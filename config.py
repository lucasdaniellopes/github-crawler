

# Configurações gerais
MAX_FILES_PER_REPO = 50
MAX_FILE_SIZE_KB = 500
TIMEOUT_SECONDS = 30
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2


GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_SEARCH_ENDPOINT = "/search/repositories"
GITHUB_CONTENTS_ENDPOINT = "/repos/{owner}/{repo}/contents"
GITHUB_RATE_LIMIT_ENDPOINT = "/rate_limit"


GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MAX_TOKENS = 2048
GEMINI_TEMPERATURE = 0.7


LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".ts", ".tsx"],
    "java": [".java"],
}

# Padrões de átomos de confusão por linguagem
CONFUSION_PATTERNS = {
    "python": [
        r"\b(lambda)\b.*:.*\b(lambda)\b",
        r"\[.*\bfor\b.*\bif\b.*\bfor\b.*\]",
        r"\beval\(.*\)",
        r"\bexec\(.*\)",
        r"\b__new__\b",
        r"\b__getattr__\b",
        r"\b__setattr__\b",
        r"\b__getattribute__\b",
        r"\b__delattr__\b",
        r"\b__slots__\b",
        r"\b__getitem__\b",
        r"\b__setitem__\b",
        r"\b__delitem__\b",
        r"\b__call__\b",
        r"\b__metaclass__\b",
        r"\b__mro__\b",
        r"\b__subclasses__\b",
        r"\bglobals\(\)\.update\(",
        r"\bsetattr\(.*,.*,.*\)",
        r"\bgetattr\(.*,.*\)",
        r"\bdel\b",
        r"\bnonlocal\b",
        r"\b:=\b",
        r"\b(is|is not)\b(?!(\s+None|\s+True|\s+False))",
        r"def\s+\w+\([^)]*=\s*(\[\]|\{\}|\(\)|\{\s*:\s*\}|\[\s*\]|\(\s*\))[^)]*\)",
        r"[^&|]\band\b[^&|].*\bor\b[^&|]|\bor\b[^&|].*\band\b[^&|]",
    ],
    "javascript": [
        r"\b==\b",
        r"\bwith\b",
        r"\beval\(",
        r"\bnew Function\(",
        r"\bdelete\b",
        r"\bvoid\b",
        r"\btypeof\b",
        r"\b\+\+\b|\b--\b",
        r"\!\!\b",
        r"\b\?\?",
    ],
    "java": [
        r"\binstanceof\b",
        r"\bassert\b",
        r"\bsynchronized\b",
        r"\bvolatile\b",
        r"\btransient\b",
        r"\bclone\(\)",
        r"\bfinalize\(\)",
        r"\bClass\.forName\(",
        r"\bReflection",
        r"\bThreadLocal\b",
    ],
}

# Palavras-chave para buscar em comentários que podem indicar código confuso
SUSPICIOUS_COMMENT_PATTERNS = [
    r"\bhack\b",
    r"\bworkaround\b",
    r"\bfixme\b",
    r"\btodo\b",
    r"\bnote:\b",
    r"\bcaution\b",
    r"\bcareful\b",
    r"\bdon't change\b",
    r"\bdon't touch\b",
    r"\bmagic\b",
    r"\btricky\b",
    r"\bcomplicated\b",
    r"\bconfusing\b",
    r"\bweird\b",
    r"\bodd\b",
    r"\bstrange\b",
    r"\bunexpected\b",
    r"\bnot intuitive\b",
]

# Comentários padrão do Django que devem ser ignorados
DJANGO_STANDARD_COMMENTS = [
    r"SECURITY WARNING: keep the secret key used in production secret",
    r"SECURITY WARNING: don't run with debug turned on in production",
]


GEMINI_PROMPTS = {
    "confusion_analysis": """Analise o seguinte código e identifique possíveis 'átomos de confusão'. 
    Átomos de confusão são pequenos fragmentos de código que parecem fazer uma coisa, mas na verdade fazem outra, 
    levando a bugs sutis e dificuldades de compreensão. 
    
    Concentre-se em:
    1. Operadores com precedência não intuitiva
    2. Efeitos colaterais inesperados
    3. Coerção de tipos confusa
    4. Uso de recursos obscuros da linguagem
    5. Construções sintáticas ambíguas
    6. Padrões que podem ser facilmente mal interpretados
    
    Para cada átomo de confusão identificado, forneça:
    - A linha e coluna onde ele ocorre
    - Uma explicação do comportamento real vs. comportamento esperado
    - Uma sugestão de como reescrever o código para torná-lo mais claro
    
    Código para análise:
    ```{language}
    {code}
    ```
    """,
    
    "code_quality": """Analise o seguinte código e forneça uma avaliação detalhada de sua qualidade, 
    focando especificamente em clareza, manutenibilidade e potencial para introduzir bugs sutis.
    
    Código para análise:
    ```{language}
    {code}
    ```
    """,
    
    "complexity_analysis": """Analise o seguinte código e avalie sua complexidade cognitiva. 
    Identifique trechos que são difíceis de entender à primeira vista e explique por que.
    
    Código para análise:
    ```{language}
    {code}
    ```
    """,
}


DEFAULT_REPO_FILTERS = {
    "min_stars": 10,
    "min_forks": 5,
    "languages": ["python", "javascript", "java"],
    "last_updated": "2023-01-01",
    "max_repo_size_kb": 50000,
}
