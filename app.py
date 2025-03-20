import os
import sys
import argparse
import json
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime

from github_api import GitHubAPI, ConfusionAtomDetector, RepositoryAnalyzer
from gemini_api import GeminiAPI
from report_generator import ReportGenerator
import config

load_dotenv()

github_token = os.getenv('GITHUB_ACCESS_TOKEN')
gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

if not github_token:
    print("Erro: Token de acesso do GitHub não encontrado no arquivo .env")
    sys.exit(1)

if not gemini_api_key:
    print("Erro: Chave de API do Google Gemini não encontrada no arquivo .env")
    sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Crawler GitHub para detectar átomos de confusão em código')
    
    parser.add_argument('--query', type=str, default="code confusion",
                        help='Termo de busca para repositórios')
    parser.add_argument('--languages', type=str, nargs='+',
                        default=["python", "javascript", "java"],
                        help='Linguagens de programação para filtrar (ex: python javascript)')
    parser.add_argument('--min-stars', type=int, default=10,
                        help='Número mínimo de estrelas para filtrar repositórios')
    parser.add_argument('--min-forks', type=int, default=5,
                        help='Número mínimo de forks para filtrar repositórios')
    parser.add_argument('--max-repos', type=int, default=5,
                        help='Número máximo de repositórios para analisar')
    parser.add_argument('--max-files', type=int, default=config.MAX_FILES_PER_REPO,
                        help='Número máximo de arquivos para analisar por repositório')
    parser.add_argument('--updated-after', type=str, default="2023-01-01",
                        help='Filtrar repositórios atualizados após esta data (YYYY-MM-DD)')
    
    parser.add_argument('--analyze-repo', type=str,
                        help='Analisar um repositório específico (formato: dono/repo)')
    parser.add_argument('--deep-analysis', action='store_true',
                        help='Realizar análise profunda com Gemini para arquivos com átomos de confusão')
    
    parser.add_argument('--output-dir', type=str, default="reports",
                        help='Diretório para salvar os relatórios')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'html', 'all'], default='all',
                        help='Formato do relatório de saída')
    
    return parser.parse_args()


def analyze_specific_repository(repo_path: str, analyzer: RepositoryAnalyzer, 
                              gemini: Optional[GeminiAPI] = None, 
                              deep_analysis: bool = False) -> Dict[str, Any]:
    try:
        owner, repo = repo_path.split('/')
    except ValueError:
        print(f"Erro: Formato inválido para repositório. Use o formato 'dono/repo'")
        return {}
    
    print(f"\nAnalisando repositório específico: {owner}/{repo}")
    result = analyzer.analyze_repository(owner, repo)
    
    if deep_analysis and gemini and result['files_with_confusion'] > 0:
        perform_deep_analysis(result, gemini)
    
    return result


def search_and_analyze_repositories(args, analyzer: RepositoryAnalyzer, 
                                   gemini: Optional[GeminiAPI] = None) -> List[Dict[str, Any]]:
    print(f"\nBuscando repositórios com o termo: {args.query}")
    print(f"Linguagens: {', '.join(args.languages)}")
    print(f"Filtros: min_stars={args.min_stars}, min_forks={args.min_forks}, updated_after={args.updated_after}")
    
    analyzer.max_files = args.max_files
    
    results = analyzer.find_repositories_with_confusion(
        query=args.query,
        languages=args.languages,
        min_stars=args.min_stars,
        min_forks=args.min_forks,
        last_updated=args.updated_after,
        max_repos=args.max_repos
    )
    
    if args.deep_analysis and gemini:
        for result in results:
            if result['files_with_confusion'] > 0:
                perform_deep_analysis(result, gemini)
    
    return results


def perform_deep_analysis(result: Dict[str, Any], gemini: GeminiAPI) -> None:
    print(f"\nRealizando análise profunda com Gemini para {len(result['files'])} arquivos...")
    
    github_api = GitHubAPI(github_token)
    
    for file_info in result['files']:
        filename = file_info.get('filename', '')
        path = file_info.get('path', '')
        language = file_info.get('language', '')
        
        repo_parts = result['repository'].split('/')
        if len(repo_parts) != 2:
            continue
        
        owner, repo = repo_parts
        
        file_content = ""
        file_url = ""
        
        file_info_api = github_api.get_repo_contents(owner, repo, path)
        
        if isinstance(file_info_api, dict) and 'download_url' in file_info_api:
            file_url = file_info_api['download_url']
            content, success = github_api.get_file_content(file_url)
            if success:
                file_content = content
        
        if not file_content:
            print(f"Não foi possível obter o conteúdo do arquivo: {path}")
            continue
        
        print(f"Analisando {filename} com Gemini...")
        
        confusion_analysis = gemini.analyze_confusion_atoms(file_content, language, filename)
        
        if confusion_analysis['success']:
            file_info['gemini_analysis'] = confusion_analysis['analysis']
        else:
            print(f"Falha na análise do Gemini para {filename}: {confusion_analysis['analysis']}")


def generate_reports(results: List[Dict[str, Any]], args) -> None:
    if not results:
        print("Nenhum resultado para gerar relatórios.")
        return
    
    report_generator = ReportGenerator(output_dir=args.output_dir)
    
    for i, result in enumerate(results):
        print(f"\nGerando relatórios para {result['repository']}...")
        
        if args.format == 'json' or args.format == 'all':
            json_path = report_generator.generate_json_report(
                result, f"repo_{i+1}_{result['repository'].replace('/', '_')}.json")
            print(f"Relatório JSON: {json_path}")
        
        if args.format == 'csv' or args.format == 'all':
            csv_path = report_generator.generate_csv_report(
                result, f"repo_{i+1}_{result['repository'].replace('/', '_')}.csv")
            print(f"Relatório CSV: {csv_path}")
        
        if args.format == 'html' or args.format == 'all':
            html_path = report_generator.generate_html_report(
                result, f"repo_{i+1}_{result['repository'].replace('/', '_')}.html")
            print(f"Relatório HTML: {html_path}")
    
    if len(results) > 1:
        print("\nGerando relatório consolidado...")
        
        consolidated = {
            'timestamp': datetime.now().isoformat(),
            'total_repositories': len(results),
            'repositories_analyzed': [result['repository'] for result in results],
            'total_files_analyzed': sum(result['files_analyzed'] for result in results),
            'total_files_with_confusion': sum(result['files_with_confusion'] for result in results),
            'average_confusion_score': sum(result['average_confusion_score'] for result in results) / len(results),
            'repositories': results
        }
        
        if args.format == 'json' or args.format == 'all':
            json_path = report_generator.generate_json_report(consolidated, "relatorio_consolidado.json")
            print(f"Relatório consolidado JSON: {json_path}")
        
        if args.format == 'html' or args.format == 'all':
            html_path = report_generator.generate_html_report(consolidated, "relatorio_consolidado.html")
            print(f"Relatório consolidado HTML: {html_path}")


def main():
    args = parse_arguments()
    
    print("Iniciando crawler GitHub para detecção de átomos de confusão")
    print(f"Token GitHub: {'Configurado' if github_token else 'Não configurado'}")
    print(f"API Key Gemini: {'Configurada' if gemini_api_key else 'Não configurada'}")
    
    github_api = GitHubAPI(github_token)
    analyzer = RepositoryAnalyzer(github_api)
    
    gemini = None
    if args.deep_analysis and gemini_api_key:
        gemini = GeminiAPI(gemini_api_key)
        print("Análise profunda com Gemini ativada")
    
    results = []
    
    if args.analyze_repo:
        result = analyze_specific_repository(args.analyze_repo, analyzer, gemini, args.deep_analysis)
        if result:
            results.append(result)
    else:
        results = search_and_analyze_repositories(args, analyzer, gemini)
    
    if results:
        generate_reports(results, args)
        print("\nAnálise concluída com sucesso!")
    else:
        print("\nNenhum resultado encontrado para gerar relatórios.")


if __name__ == "__main__":
    main()
