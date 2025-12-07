#!/usr/bin/env python3
"""
Script para gerar relatório analítico completo do projeto
"""
import os
import json
import subprocess
import datetime
from pathlib import Path

def run_command(cmd):
    """Executa comando e retorna saída"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def analyze_project():
    """Analisa estrutura do projeto"""
    print("🔬 Analisando estrutura do projeto...")
    
    # Coletar dados
    stats = {
        'date': datetime.datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
        'iso_date': datetime.datetime.now().isoformat(),
        'files': {}
    }
    
    # Contar arquivos por tipo
    extensions = ['.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.gif', '.svg']
    for ext in extensions:
        result = run_command(f"find . -name '*{ext}' -type f | wc -l")
        stats['files'][ext] = int(result) if result.isdigit() else 0
    
    # Linhas de código
    stats['lines'] = {
        'html': int(run_command("find . -name '*.html' | xargs cat 2>/dev/null | wc -l") or 0),
        'css': int(run_command("find . -name '*.css' | xargs cat 2>/dev/null | wc -l") or 0),
        'js': int(run_command("find . -name '*.js' | xargs cat 2>/dev/null | wc -l") or 0),
        'total': int(run_command("find . -name '*.html' -o -name '*.css' -o -name '*.js' | xargs cat 2>/dev/null | wc -l") or 0)
    }
    
    # Estrutura de árvore
    stats['tree'] = run_command("tree -a -I '.git|node_modules|__pycache__' --charset=utf-8 2>/dev/null || echo 'tree não disponível'")
    
    # Módulos
    stats['modules'] = {
        'js_modules': run_command("find js/modules -name '*.js' -type f 2>/dev/null | xargs -I {} basename {} .js | tr '\n' ',' | sed 's/,$//'") or "Não encontrado",
        'js_components': run_command("find js/components -name '*.js' -type f 2>/dev/null | xargs -I {} basename {} .js | tr '\n' ',' | sed 's/,$//'") or "Não encontrado"
    }
    
    return stats

def generate_html_report(stats, output_file):
    """Gera relatório HTML"""
    print(f"📝 Gerando relatório HTML em {output_file}...")
    
    html_template = f'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 Relatório Analítico - Imóveis Maceió</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #2ea44f;
            --secondary: #24292e;
            --dark: #0d1117;
            --light: #c9d1d9;
            --card: #161b22;
            --border: #30363d;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--dark);
            color: var(--light);
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid var(--primary);
        }}
        h1 {{ color: var(--primary); font-size: 2.5em; }}
        h2 {{ color: #58a6ff; margin: 30px 0 15px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }}
        h3 {{ color: var(--primary); margin: 20px 0 10px; }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 25px;
            transition: transform 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-box {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.8em;
            font-weight: bold;
            color: var(--primary);
            line-height: 1;
        }}
        .stat-label {{
            margin-top: 10px;
            color: #8b949e;
            font-size: 0.9em;
        }}
        
        .file-tree {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 500px;
            overflow-y: auto;
        }}
        
        nav {{
            background: var(--card);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            position: sticky;
            top: 10px;
            z-index: 100;
        }}
        nav a {{
            color: var(--light);
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 12px;
            border-radius: 6px;
            transition: all 0.3s;
        }}
        nav a:hover {{
            background: var(--primary);
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .dashboard, .stats-grid {{
                grid-template-columns: 1fr;
            }}
            nav {{ position: static; }}
            nav a {{ display: block; margin: 5px 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-file-alt"></i> Relatório Analítico Completo</h1>
            <h2>Imóveis Maceió - Sistema de Gestão de Imóveis</h2>
            <p><strong>Gerado em:</strong> {stats['date']}</p>
            <p><small>Análise estrutural e técnica do projeto completo</small></p>
        </header>
        
        <nav>
            <a href="#overview"><i class="fas fa-eye"></i> Visão Geral</a>
            <a href="#stats"><i class="fas fa-chart-bar"></i> Estatísticas</a>
            <a href="#structure"><i class="fas fa-sitemap"></i> Estrutura</a>
            <a href="https://rclessa25-hub.github.io/imoveis-maceio/" target="_blank">
                <i class="fas fa-external-link-alt"></i> Site Principal
            </a>
        </nav>
        
        <section id="overview">
            <h2><i class="fas fa-globe"></i> Visão Geral</h2>
            <div class="dashboard">
                <div class="card">
                    <h3><i class="fas fa-info-circle"></i> Informações</h3>
                    <p><strong>Nome:</strong> Imóveis Maceió</p>
                    <p><strong>Status:</strong> Ativo</p>
                    <p><strong>Hospedagem:</strong> GitHub Pages</p>
                </div>
                
                <div class="card">
                    <h3><i class="fas fa-cogs"></i> Tecnologias</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        <span style="background: #e34c26; color: white; padding: 5px 10px; border-radius: 4px;">HTML5</span>
                        <span style="background: #563d7c; color: white; padding: 5px 10px; border-radius: 4px;">CSS3</span>
                        <span style="background: #f1e05a; color: black; padding: 5px 10px; border-radius: 4px;">JavaScript</span>
                        <span style="background: #3fb27f; color: white; padding: 5px 10px; border-radius: 4px;">Supabase</span>
                    </div>
                </div>
            </div>
        </section>
        
        <section id="stats">
            <h2><i class="fas fa-chart-bar"></i> Estatísticas</h2>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-number">{sum(stats['files'].values())}</div>
                    <div class="stat-label">Total de Arquivos</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{stats['lines']['total']}</div>
                    <div class="stat-label">Linhas de Código</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{stats['files']['.html']}</div>
                    <div class="stat-label">Arquivos HTML</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{stats['files']['.css']}</div>
                    <div class="stat-label">Arquivos CSS</div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-number">{stats['files']['.js']}</div>
                    <div class="stat-label">Arquivos JS</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{stats['files']['.json']}</div>
                    <div class="stat-label">Arquivos JSON</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{stats['files']['.png'] + stats['files']['.jpg'] + stats['files']['.jpeg']}</div>
                    <div class="stat-label">Imagens</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">✅</div>
                    <div class="stat-label">Status</div>
                </div>
            </div>
            
            <div class="card">
                <h3><i class="fas fa-chart-pie"></i> Distribuição</h3>
                <canvas id="fileChart" width="400" height="200"></canvas>
            </div>
        </section>
        
        <section id="structure">
            <h2><i class="fas fa-sitemap"></i> Estrutura do Projeto</h2>
            
            <div class="card">
                <h3><i class="fas fa-folder-tree"></i> Hierarquia</h3>
                <div class="file-tree">
                    <pre>{stats['tree']}</pre>
                </div>
            </div>
            
            <div class="card">
                <h3><i class="fas fa-code-branch"></i> Módulos</h3>
                <p><strong>Módulos JS:</strong> {stats['modules']['js_modules']}</p>
                <p><strong>Componentes:</strong> {stats['modules']['js_components']}</p>
            </div>
        </section>
        
        <footer style="margin-top: 50px; text-align: center; padding-top: 20px; border-top: 1px solid var(--border);">
            <p>Relatório gerado automaticamente por GitHub Actions</p>
            <p>Atualizado em: {stats['date']}</p>
            <p>
                <a href="https://rclessa25-hub.github.io/imoveis-maceio/" style="color: var(--primary);">Site Principal</a> | 
                <a href="https://github.com/rclessa25-hub/imoveis-maceio" style="color: var(--primary);">Repositório</a>
            </p>
        </footer>
    </div>
    
    <script>
        // Gráfico
        const ctx = document.getElementById('fileChart').getContext('2d');
        new Chart(ctx, {{
            type: 'pie',
            data: {{
                labels: ['HTML', 'CSS', 'JS', 'JSON', 'Imagens'],
                datasets: [{{
                    data: [
                        {stats['files']['.html']},
                        {stats['files']['.css']},
                        {stats['files']['.js']},
                        {stats['files']['.json']},
                        {stats['files']['.png'] + stats['files']['.jpg'] + stats['files']['.jpeg'] + stats['files']['.gif'] + stats['files']['.svg']}
                    ],
                    backgroundColor: ['#e34c26', '#563d7c', '#f1e05a', '#f1e05a', '#0366d6']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Navegação suave
        document.querySelectorAll('nav a').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                if(this.getAttribute('href').startsWith('#')) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {{
                        window.scrollTo({{
                            top: targetElement.offsetTop - 80,
                            behavior: 'smooth'
                        }});
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("✅ Relatório HTML gerado com sucesso!")

def main():
    """Função principal"""
    print("🚀 Iniciando geração de relatório analítico...")
    
    # Analisar projeto
    stats = analyze_project()
    
    # Salvar dados em JSON
    with open('project_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Gerar relatório HTML
    generate_html_report(stats, 'index.html')
    
    print("🎉 Relatório completo gerado!")
    print(f"📊 Estatísticas salvas em: project_stats.json")
    print(f"📄 Relatório HTML: index.html")

if __name__ == "__main__":
    main()
