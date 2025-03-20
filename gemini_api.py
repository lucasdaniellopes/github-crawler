import requests
import time
import os
from typing import Dict, List, Any, Optional, Tuple
import config

class GeminiAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = config.GEMINI_MODEL
        self.base_url = config.GEMINI_API_URL.format(model=self.model)
        self.max_tokens = config.GEMINI_MAX_TOKENS
        self.temperature = config.GEMINI_TEMPERATURE
        self.retry_attempts = config.RETRY_ATTEMPTS
        self.retry_delay = config.RETRY_DELAY
        self.timeout = config.TIMEOUT_SECONDS
    
    def _make_request(self, prompt: str) -> Dict[str, Any]:
        url = f"{self.base_url}?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": self.max_tokens
            }
        }
        
        current_attempt = 0
        while current_attempt < self.retry_attempts:
            try:
                print(f"Enviando requisição para o Gemini...")
                response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Erro na requisição ao Gemini: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"Erro de requisição ao Gemini: {str(e)}")
            
            sleep_time = self.retry_delay * (2 ** current_attempt)
            print(f"Tentativa {current_attempt + 1} falhou. Aguardando {sleep_time} segundos...")
            time.sleep(sleep_time)
            current_attempt += 1
        
        print("Todas as tentativas falharam para a API do Gemini")
        return {}
    
    def analyze_code(self, code: str, language: str, analysis_type: str = "confusion_analysis") -> Dict[str, Any]:
        if analysis_type not in config.GEMINI_PROMPTS:
            analysis_type = "confusion_analysis"
        
        prompt_template = config.GEMINI_PROMPTS[analysis_type]
        
        max_code_length = 10000
        if len(code) > max_code_length:
            code = code[:max_code_length] + "\n\n... [código truncado devido ao tamanho] ..."
        
        prompt = prompt_template.format(language=language, code=code)
        
        response = self._make_request(prompt)
        
        if not response:
            return {
                "success": False,
                "analysis": "Falha ao analisar o código com o Gemini."
            }
        
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                return {
                    "success": False,
                    "analysis": "Não foi possível obter uma resposta do Gemini."
                }
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return {
                    "success": False,
                    "analysis": "Resposta vazia do Gemini."
                }
            
            analysis_text = parts[0].get("text", "")
            
            return {
                "success": True,
                "analysis": analysis_text,
                "analysis_type": analysis_type
            }
        except Exception as e:
            print(f"Erro ao processar resposta do Gemini: {str(e)}")
            return {
                "success": False,
                "analysis": f"Erro ao processar resposta: {str(e)}"
            }
    
    def analyze_confusion_atoms(self, code: str, language: str, filename: str) -> Dict[str, Any]:
        print(f"Analisando átomos de confusão em: {filename}")
        return self.analyze_code(code, language, "confusion_analysis")
    
    def analyze_code_quality(self, code: str, language: str, filename: str) -> Dict[str, Any]:
        print(f"Analisando qualidade do código em: {filename}")
        return self.analyze_code(code, language, "code_quality")
    
    def analyze_complexity(self, code: str, language: str, filename: str) -> Dict[str, Any]:
        print(f"Analisando complexidade do código em: {filename}")
        return self.analyze_code(code, language, "complexity_analysis")
