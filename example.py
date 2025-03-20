#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from typing import Dict, List, Any

def verify_environment_variables():
    if not os.getenv('GITHUB_ACCESS_TOKEN') or not os.getenv('GOOGLE_GEMINI_API_KEY'):
        print("Erro: Variáveis de ambiente não configuradas.")
        print("Certifique-se de que GITHUB_ACCESS_TOKEN e GOOGLE_GEMINI_API_KEY estão definidas no arquivo .env")
        sys.exit(1)

def get_examples() -> List[Dict[str, Any]]:
    return [
        {
            "name": "Análise Básica",
            "description": "Busca repositórios Python com pelo menos 100 estrelas",
            "command": "python app.py --query \"python code\" --languages python --min-stars 100 --max-repos 2 --max-files 10"
        },
        {
            "name": "Análise Profunda",
            "description": "Analisa um repositório específico com análise profunda usando Gemini",
            "command": "python app.py --analyze-repo \"facebook/react\" --max-files 5 --deep-analysis"
        },
        {
            "name": "Busca por Átomos de Confusão",
            "description": "Busca repositórios JavaScript com potenciais átomos de confusão",
            "command": "python app.py --query \"complex javascript\" --languages javascript --min-stars 50 --max-repos 3 --max-files 15"
        },
        {
            "name": "Relatório HTML",
            "description": "Gera apenas relatórios HTML para um repositório específico",
            "command": "python app.py --analyze-repo \"tensorflow/tensorflow\" --max-files 5 --format html"
        }
    ]

def display_examples(examples: List[Dict[str, Any]]):
    print("\n===== GitHub Crawler para Átomos de Confusão - Exemplos =====\n")
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}")
        print(f"   {example['description']}")
        print(f"   Comando: {example['command']}")
        print()

def get_user_choice(max_choice: int) -> int:
    try:
        choice = int(input(f"Escolha um exemplo para executar (1-{max_choice}) ou 0 para sair: "))
        if 0 <= choice <= max_choice:
            return choice
        
        print("Opção inválida!")
        return get_user_choice(max_choice)
    except ValueError:
        print("Por favor, digite um número válido.")
        return get_user_choice(max_choice)

def execute_example(example: Dict[str, Any]):
    print(f"\nExecutando: {example['name']}")
    print(f"Comando: {example['command']}")
    print("\n" + "-"*50 + "\n")
    
    subprocess.run(example['command'], shell=True)

def main():
    verify_environment_variables()
    
    examples = get_examples()
    display_examples(examples)
    
    choice = get_user_choice(len(examples))
    
    if choice == 0:
        print("Saindo...")
        sys.exit(0)
    
    execute_example(examples[choice-1])

if __name__ == "__main__":
    main()
