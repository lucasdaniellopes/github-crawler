import requests
import time
import re
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import config

class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.headers = {'Authorization': f'token {token}'}
        self.base_url = config.GITHUB_API_BASE_URL
        self.retry_attempts = config.RETRY_ATTEMPTS
        self.retry_delay = config.RETRY_DELAY
        self.timeout = config.TIMEOUT_SECONDS
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        current_attempt = 0
        while current_attempt < self.retry_attempts:
            try:
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining == 0:
                        reset_time = int(response.headers['X-RateLimit-Reset'])
                        sleep_time = reset_time - int(time.time()) + 1
                        if sleep_time > 0:
                            print(f"Limite de taxa atingido. Aguardando {sleep_time} segundos...")
                            time.sleep(sleep_time)
                            continue
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print(f"Recurso não encontrado: {url}")
                    return {}
                else:
                    print(f"Erro na requisição: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"Erro de requisição: {str(e)}")
            
            sleep_time = self.retry_delay * (2 ** current_attempt)
            print(f"Tentativa {current_attempt + 1} falhou. Aguardando {sleep_time} segundos...")
            time.sleep(sleep_time)
            current_attempt += 1
        
        print(f"Todas as tentativas falharam para: {url}")
        return {}
    
    def check_rate_limit(self) -> Dict[str, Any]:
        url = f"{self.base_url}{config.GITHUB_RATE_LIMIT_ENDPOINT}"
        return self._make_request(url)
    
    def search_repositories(self, 
                           query: str, 
                           language: Optional[str] = None,
                           min_stars: int = 0,
                           min_forks: int = 0,
                           last_updated: Optional[str] = None,
                           page: int = 1,
                           per_page: int = 30) -> List[Dict[str, Any]]:
        url = f"{self.base_url}{config.GITHUB_SEARCH_ENDPOINT}"
        
        search_query = query
        if language:
            search_query += f" language:{language}"
        if min_stars > 0:
            search_query += f" stars:>={min_stars}"
        if min_forks > 0:
            search_query += f" forks:>={min_forks}"
        if last_updated:
            search_query += f" pushed:>={last_updated}"
        
        params = {
            'q': search_query,
            'sort': 'stars',
            'order': 'desc',
            'page': page,
            'per_page': per_page
        }
        
        result = self._make_request(url, params)
        return result.get('items', [])
    
    def get_repo_contents(self, owner: str, repo: str, path: str = '') -> List[Dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        return self._make_request(url)
    
    def get_file_content(self, file_url: str) -> Tuple[str, bool]:
        try:
            response = requests.get(file_url, timeout=self.timeout)
            if response.status_code == 200:
                return response.text, True
            else:
                print(f"Erro ao obter conteúdo do arquivo: {response.status_code}")
                return "", False
        except requests.RequestException as e:
            print(f"Erro ao obter conteúdo do arquivo: {str(e)}")
            return "", False


class ConfusionAtomDetector:
    def __init__(self):
        self.patterns = config.CONFUSION_PATTERNS
        self.comment_patterns = config.SUSPICIOUS_COMMENT_PATTERNS
        self.django_standard_comments = getattr(config, 'DJANGO_STANDARD_COMMENTS', [])
        self.language_extensions = config.LANGUAGE_EXTENSIONS
    
    def detect_language_from_extension(self, filename: str) -> Optional[str]:
        _, ext = os.path.splitext(filename.lower())
        
        for language, extensions in self.language_extensions.items():
            if ext in extensions:
                return language
        
        return None
    
    def is_comment(self, line: str, language: str) -> bool:
        if language == 'python':
            return line.strip().startswith('#')
        elif language == 'java':
            return line.strip().startswith('//') or line.strip().startswith('/*')
        elif language == 'javascript':
            return line.strip().startswith('//') or line.strip().startswith('/*')
        else:
            return False
    
    def has_confusion_patterns(self, content: str, language: str) -> List[Dict[str, Any]]:
        if language not in self.patterns:
            return []
        
        results = []
        lines = content.split('\n')
        
        for pattern in self.patterns.get(language, []):
            for i, line in enumerate(lines):
                if not self.is_comment(line, language):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        results.append({
                            'type': 'confusion_pattern',
                            'pattern': pattern,
                            'line_number': i + 1,
                            'line_content': line.strip(),
                            'match': match.group(0),
                            'start_col': match.start(),
                            'end_col': match.end()
                        })
        
        for pattern in self.comment_patterns:
            for i, line in enumerate(lines):
                if any(django_comment in line for django_comment in self.django_standard_comments):
                    continue
                
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    results.append({
                        'type': 'suspicious_comment',
                        'pattern': pattern,
                        'line_number': i + 1,
                        'line_content': line.strip(),
                        'match': match.group(0),
                        'start_col': match.start(),
                        'end_col': match.end()
                    })
        
        return results
    
    def calculate_confusion_score(self, results: List[Dict[str, Any]], content_length: int) -> float:
        if content_length == 0:
            return 0.0
        
        weights = {
            'confusion_pattern': 2.0,
            'suspicious_comment': 1.0
        }
        
        score = sum(weights.get(result['type'], 0.0) for result in results)
        
        normalized_score = score / (content_length / 100.0)
        
        return min(normalized_score, 10.0)  


class RepositoryAnalyzer:
    def __init__(self, github_api: GitHubAPI):
        self.github_api = github_api
        self.detector = ConfusionAtomDetector()
        self.max_files = config.MAX_FILES_PER_REPO
        self.max_file_size = config.MAX_FILE_SIZE_KB * 1024  
    
    def _should_analyze_file(self, file_info: Dict[str, Any]) -> bool:
        if file_info.get('type') != 'file':
            return False
        
        if not file_info.get('download_url'):
            return False
        
        if file_info.get('size', 0) > self.max_file_size:
            return False
        
        filename = file_info.get('name', '')
        language = self.detector.detect_language_from_extension(filename)
        if not language:
            return False
        
        return True
    
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        print(f"Analisando repositório: {owner}/{repo}")
        
        results = {
            'repository': f"{owner}/{repo}",
            'analyzed_at': datetime.now().isoformat(),
            'files_analyzed': 0,
            'files_with_confusion': 0,
            'total_confusion_patterns': 0,
            'total_suspicious_comments': 0,
            'average_confusion_score': 0.0,
            'files': []
        }
        
        contents = self.github_api.get_repo_contents(owner, repo)
        if not contents:
            print(f"Nenhum conteúdo encontrado para {owner}/{repo}")
            return results
        
        files_to_analyze = []
        
        queue = [item for item in contents if isinstance(item, dict)]
        
        while queue and len(files_to_analyze) < self.max_files:
            item = queue.pop(0)
            
            if item.get('type') == 'dir':
                dir_contents = self.github_api.get_repo_contents(owner, repo, item.get('path', ''))
                if isinstance(dir_contents, list):
                    queue.extend(dir_contents)
            elif self._should_analyze_file(item):
                files_to_analyze.append(item)
        
        files_to_analyze = files_to_analyze[:self.max_files]
        
        total_confusion_score = 0.0
        
        for file_info in files_to_analyze:
            filename = file_info.get('name', '')
            file_path = file_info.get('path', '')
            file_url = file_info.get('download_url', '')
            language = self.detector.detect_language_from_extension(filename)
            
            print(f"Analisando arquivo: {file_path}")
            
            content, success = self.github_api.get_file_content(file_url)
            if not success or not content:
                print(f"Falha ao obter conteúdo do arquivo: {file_path}")
                continue
            
            confusion_results = self.detector.has_confusion_patterns(content, language)
            
            confusion_score = self.detector.calculate_confusion_score(confusion_results, len(content.split('\n')))
            total_confusion_score += confusion_score
            
            confusion_patterns = sum(1 for r in confusion_results if r['type'] == 'confusion_pattern')
            suspicious_comments = sum(1 for r in confusion_results if r['type'] == 'suspicious_comment')
            
            if confusion_results:
                results['files_with_confusion'] += 1
                results['total_confusion_patterns'] += confusion_patterns
                results['total_suspicious_comments'] += suspicious_comments
                
                results['files'].append({
                    'filename': filename,
                    'path': file_path,
                    'language': language,
                    'confusion_score': confusion_score,
                    'confusion_patterns': confusion_patterns,
                    'suspicious_comments': suspicious_comments,
                    'details': confusion_results
                })
            
            results['files_analyzed'] += 1
        
        if results['files_analyzed'] > 0:
            results['average_confusion_score'] = total_confusion_score / results['files_analyzed']
        
        results['files'] = sorted(results['files'], key=lambda x: x['confusion_score'], reverse=True)
        
        return results
    
    def find_repositories_with_confusion(self, 
                                        query: str,
                                        languages: List[str] = None,
                                        min_stars: int = 10,
                                        min_forks: int = 5,
                                        last_updated: str = None,
                                        max_repos: int = 5) -> List[Dict[str, Any]]:
        if languages is None:
            languages = list(config.CONFUSION_PATTERNS.keys())
        
        all_results = []
        
        for language in languages:
            print(f"Buscando repositórios para a linguagem: {language}")
            
            repos = self.github_api.search_repositories(
                query=query,
                language=language,
                min_stars=min_stars,
                min_forks=min_forks,
                last_updated=last_updated,
                per_page=max_repos
            )
            
            for repo in repos:
                owner = repo.get('owner', {}).get('login')
                repo_name = repo.get('name')
                
                if owner and repo_name:
                    result = self.analyze_repository(owner, repo_name)
                    all_results.append(result)
                    
                    if len(all_results) >= max_repos:
                        break
            
            if len(all_results) >= max_repos:
                break
        
        all_results = sorted(all_results, key=lambda x: x['average_confusion_score'], reverse=True)
        
        return all_results
