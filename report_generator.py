import json
import csv
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self._create_output_dir()

    def _create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_json_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        if filename is None:
            timestamp = self._get_timestamp()
            filename = f"relatorio_de_atomo_de_confusao_{timestamp}.json"
        
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        print(f"Relatório JSON gerado: {file_path}")
        return file_path

    def generate_csv_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        if filename is None:
            timestamp = self._get_timestamp()
            filename = f"relatorio_de_atomo_de_confusao_{timestamp}.csv"
        
        file_path = os.path.join(self.output_dir, filename)
        
        files_data = []
        repository = data.get('repository', 'N/A')
        
        for file_info in data.get('files', []):
            file_entry = {
                'Repositório': repository,
                'Nome do Arquivo': file_info.get('filename', 'N/A'),
                'Caminho': file_info.get('path', 'N/A'),
                'Linguagem': file_info.get('language', 'N/A'),
                'Pontuação de Confusão': file_info.get('confusion_score', 0.0),
                'Padrões de Confusão': file_info.get('confusion_patterns', 0),
                'Comentários Suspeitos': file_info.get('suspicious_comments', 0)
            }
            files_data.append(file_entry)
        
        if files_data:
            with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
                fieldnames = list(files_data[0].keys())
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for file_entry in files_data:
                    writer.writerow(file_entry)
            
            print(f"Relatório CSV gerado: {file_path}")
        else:
            print("Nenhum dado de arquivo para gerar relatório CSV")
        
        return file_path

    def generate_html_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        if filename is None:
            timestamp = self._get_timestamp()
            filename = f"relatorio_de_atomo_de_confusao_{timestamp}.html"
        
        file_path = os.path.join(self.output_dir, filename)
        
        repository = data.get('repository', 'N/A')
        analyzed_at = data.get('analyzed_at', datetime.now().isoformat())
        files_analyzed = data.get('files_analyzed', 0)
        files_with_confusion = data.get('files_with_confusion', 0)
        average_confusion_score = data.get('average_confusion_score', 0.0)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Átomos de Confusão - {repository}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .file-card {{ border: 1px solid #ddd; border-radius: 5px; margin-bottom: 15px; padding: 15px; }}
                .file-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
                .score {{ font-weight: bold; }}
                .high-score {{ color: #d9534f; }}
                .medium-score {{ color: #f0ad4e; }}
                .low-score {{ color: #5cb85c; }}
                .pattern {{ background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #007bff; }}
                .comment {{ background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #6c757d; }}
                .gemini-analysis {{ background-color: #e9f7fe; padding: 15px; margin: 15px 0; border-left: 3px solid #17a2b8; border-radius: 5px; }}
                .line-content {{ font-family: monospace; white-space: pre-wrap; background-color: #f8f9fa; padding: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .toggle-button {{ background-color: #17a2b8; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; margin-top: 10px; }}
                .toggle-button:hover {{ background-color: #138496; }}
                .hidden {{ display: none; }}
            </style>
            <script>
                function toggleGeminiAnalysis(id) {{
                    const analysis = document.getElementById(id);
                    const button = document.getElementById(id + '-button');
                    if (analysis.classList.contains('hidden')) {{
                        analysis.classList.remove('hidden');
                        button.textContent = 'Ocultar Análise do Gemini';
                    }} else {{
                        analysis.classList.add('hidden');
                        button.textContent = 'Mostrar Análise do Gemini';
                    }}
                }}
            </script>
        </head>
        <body>
            <h1>Relatório de Átomos de Confusão</h1>
            
            <div class="summary">
                <h2>Resumo</h2>
                <p><strong>Repositório:</strong> {repository}</p>
                <p><strong>Data da Análise:</strong> {analyzed_at}</p>
                <p><strong>Arquivos Analisados:</strong> {files_analyzed}</p>
                <p><strong>Arquivos com Átomos de Confusão:</strong> {files_with_confusion}</p>
                <p><strong>Pontuação Média de Confusão:</strong> {average_confusion_score:.2f}/10.0</p>
            </div>
            
            <h2>Arquivos Analisados</h2>
        """
        
        html_content += """
            <table>
                <tr>
                    <th>Arquivo</th>
                    <th>Linguagem</th>
                    <th>Pontuação de Confusão</th>
                    <th>Padrões de Confusão</th>
                    <th>Comentários Suspeitos</th>
                </tr>
        """
        
        for file_info in data.get('files', []):
            filename = file_info.get('filename', 'N/A')
            language = file_info.get('language', 'N/A')
            confusion_score = file_info.get('confusion_score', 0.0)
            confusion_patterns = file_info.get('confusion_patterns', 0)
            suspicious_comments = file_info.get('suspicious_comments', 0)
            
            score_class = "low-score"
            if confusion_score >= 7.0:
                score_class = "high-score"
            elif confusion_score >= 4.0:
                score_class = "medium-score"
            
            html_content += f"""
                <tr>
                    <td>{filename}</td>
                    <td>{language}</td>
                    <td class="{score_class}">{confusion_score:.2f}/10.0</td>
                    <td>{confusion_patterns}</td>
                    <td>{suspicious_comments}</td>
                </tr>
            """
        
        html_content += "</table>"
        
        html_content += "<h2>Detalhes dos Átomos de Confusão</h2>"
        
        for i, file_info in enumerate(data.get('files', [])):
            filename = file_info.get('filename', 'N/A')
            path = file_info.get('path', 'N/A')
            language = file_info.get('language', 'N/A')
            confusion_score = file_info.get('confusion_score', 0.0)
            gemini_analysis = file_info.get('gemini_analysis', '')
            
            score_class = "low-score"
            if confusion_score >= 7.0:
                score_class = "high-score"
            elif confusion_score >= 4.0:
                score_class = "medium-score"
            
            html_content += f"""
            <div class="file-card">
                <div class="file-header">
                    <h3>{filename}</h3>
                    <span class="score {score_class}">{confusion_score:.2f}/10.0</span>
                </div>
                <p><strong>Caminho:</strong> {path}</p>
                <p><strong>Linguagem:</strong> {language}</p>
            """
            
            results = file_info.get('results', [])
            
            if results:
                html_content += "<h4>Padrões de Confusão Detectados</h4>"
                
                confusion_patterns = [r for r in results if r['type'] == 'confusion_pattern']
                suspicious_comments = [r for r in results if r['type'] == 'suspicious_comment']
                
                if confusion_patterns:
                    html_content += "<h5>Padrões de Código</h5>"
                    for pattern in confusion_patterns:
                        html_content += f"""
                        <div class="pattern">
                            <p><strong>Linha {pattern['line_number']}:</strong></p>
                            <p class="line-content">{pattern['line_content']}</p>
                            <p><strong>Padrão:</strong> {pattern['pattern']}</p>
                        </div>
                        """
                
                if suspicious_comments:
                    html_content += "<h5>Comentários Suspeitos</h5>"
                    for comment in suspicious_comments:
                        html_content += f"""
                        <div class="comment">
                            <p><strong>Linha {comment['line_number']}:</strong></p>
                            <p class="line-content">{comment['line_content']}</p>
                            <p><strong>Padrão:</strong> {comment['pattern']}</p>
                        </div>
                        """
            
            if gemini_analysis:
                html_content += f"""
                <button id="gemini-{i}-button" class="toggle-button" onclick="toggleGeminiAnalysis('gemini-{i}')">Mostrar Análise do Gemini</button>
                <div id="gemini-{i}" class="gemini-analysis hidden">
                    <h4>Análise Detalhada do Gemini</h4>
                    <pre>{gemini_analysis}</pre>
                </div>
                """
            
            html_content += "</div>\n"
        
        html_content += """
            </body>
            </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)
        
        print(f"Relatório HTML gerado: {file_path}")
        return file_path

    def generate_all_reports(self, data: Dict[str, Any]) -> Dict[str, str]:
        timestamp = self._get_timestamp()
        base_filename = f"relatorio_de_atomo_de_confusao_{timestamp}"
        
        reports = {}
        reports['json'] = self.generate_json_report(data, f"{base_filename}.json")
        reports['csv'] = self.generate_csv_report(data, f"{base_filename}.csv")
        reports['html'] = self.generate_html_report(data, f"{base_filename}.html")
        
        return reports
