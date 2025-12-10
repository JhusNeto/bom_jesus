#!/usr/bin/env python3
"""
Gerador de Relatórios de Testes - Sistema Operacional Bom Jesus
Consolida resultados e gera relatório em Markdown
"""
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


def load_test_results(input_file: str) -> List[Dict[str, Any]]:
    """Carrega resultados dos testes do arquivo JSON"""
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            # Se for uma lista, retorna; se for dict, converte para lista
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "tests" in data:
                return data["tests"]
            else:
                return [data]
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        sys.exit(1)


def categorize_problems(tests: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Categoriza problemas por criticidade"""
    problems = {
        "CRITICO": [],
        "ALTO": [],
        "MEDIO": [],
        "BAIXO": []
    }
    
    for test in tests:
        if test.get("status") == "FAILED":
            category = test.get("category", "unknown")
            error = test.get("error", "Erro desconhecido")
            
            # Determinar criticidade baseado na categoria e tipo de erro
            if category in ["infrastructure", "database"]:
                problems["CRITICO"].append(test)
            elif category in ["auth", "api_basic"]:
                problems["ALTO"].append(test)
            elif category in ["api", "redis"]:
                problems["MEDIO"].append(test)
            else:
                problems["BAIXO"].append(test)
    
    return problems


def generate_markdown_report(tests: List[Dict[str, Any]], output_file: str):
    """Gera relatório em Markdown"""
    total = len(tests)
    passed = sum(1 for t in tests if t.get("status") == "PASSED")
    failed = sum(1 for t in tests if t.get("status") == "FAILED")
    skipped = sum(1 for t in tests if t.get("status") == "SKIPPED")
    
    # Agrupar por categoria
    by_category = defaultdict(list)
    for test in tests:
        category = test.get("category", "unknown")
        by_category[category].append(test)
    
    # Categorizar problemas
    problems = categorize_problems(tests)
    
    # Calcular taxa de sucesso
    success_rate = (passed / total * 100) if total > 0 else 0
    
    # Gerar Markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Testes - Sistema Operacional Bom Jesus\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Resumo Executivo
        f.write("## 📊 Resumo Executivo\n\n")
        f.write(f"- **Total de Testes:** {total}\n")
        f.write(f"- **✅ Passaram:** {passed}\n")
        f.write(f"- **❌ Falharam:** {failed}\n")
        f.write(f"- **⏭️  Pulados:** {skipped}\n")
        f.write(f"- **Taxa de Sucesso:** {success_rate:.1f}%\n\n")
        
        # Status geral
        if failed == 0:
            f.write("### ✅ Status: **TODOS OS TESTES PASSARAM**\n\n")
        else:
            f.write(f"### ⚠️  Status: **{failed} TESTE(S) FALHARAM**\n\n")
        
        # Resultados por Categoria
        f.write("## 📋 Resultados por Categoria\n\n")
        for category in sorted(by_category.keys()):
            category_tests = by_category[category]
            cat_passed = sum(1 for t in category_tests if t.get("status") == "PASSED")
            cat_failed = sum(1 for t in category_tests if t.get("status") == "FAILED")
            cat_total = len(category_tests)
            
            f.write(f"### {category.replace('_', ' ').title()}\n\n")
            f.write(f"- Total: {cat_total}\n")
            f.write(f"- ✅ Passaram: {cat_passed}\n")
            f.write(f"- ❌ Falharam: {cat_failed}\n\n")
            
            # Listar testes falhados desta categoria
            if cat_failed > 0:
                f.write("**Testes que falharam:**\n\n")
                for test in category_tests:
                    if test.get("status") == "FAILED":
                        error = test.get("error", "Erro desconhecido")
                        f.write(f"- ❌ **{test.get('name', 'Unknown')}**\n")
                        f.write(f"  - Erro: `{error[:200]}`\n\n")
        
        # Problemas Encontrados
        if failed > 0:
            f.write("## 🐛 Problemas Encontrados\n\n")
            
            for severity in ["CRITICO", "ALTO", "MEDIO", "BAIXO"]:
                if problems[severity]:
                    f.write(f"### {severity}\n\n")
                    for test in problems[severity]:
                        f.write(f"- **{test.get('name', 'Unknown')}**\n")
                        f.write(f"  - Categoria: `{test.get('category', 'unknown')}`\n")
                        error = test.get("error", "Erro desconhecido")
                        f.write(f"  - Erro: `{error[:300]}`\n\n")
        
        # Sugestões de Correção
        if failed > 0:
            f.write("## 🔧 Sugestões de Correção\n\n")
            
            # Sugestões baseadas nos tipos de erro
            if any(t.get("category") == "infrastructure" and t.get("status") == "FAILED" for t in tests):
                f.write("### Infraestrutura\n")
                f.write("- Verificar se todos os containers Docker estão rodando\n")
                f.write("- Verificar health checks dos containers\n")
                f.write("- Verificar portas expostas\n\n")
            
            if any(t.get("category") == "database" and t.get("status") == "FAILED" for t in tests):
                f.write("### Banco de Dados\n")
                f.write("- Verificar conexão com PostgreSQL\n")
                f.write("- Verificar se migrations foram aplicadas: `alembic upgrade head`\n")
                f.write("- Verificar se usuário de teste existe: `python scripts/create-test-user.py`\n\n")
            
            if any(t.get("category") == "auth" and t.get("status") == "FAILED" for t in tests):
                f.write("### Autenticação\n")
                f.write("- Verificar se usuário de teste existe no banco\n")
                f.write("- Verificar configuração de JWT (SECRET_KEY)\n")
                f.write("- Verificar conexão com Redis para refresh tokens\n\n")
            
            if any(t.get("category") == "redis" and t.get("status") == "FAILED" for t in tests):
                f.write("### Redis\n")
                f.write("- Verificar se Redis está rodando\n")
                f.write("- Verificar conexão: `docker exec bom_jesus_redis_dev redis-cli ping`\n\n")
        
        # Detalhes dos Testes
        f.write("## 📝 Detalhes dos Testes\n\n")
        f.write("| Teste | Status | Categoria |\n")
        f.write("|-------|--------|-----------|\n")
        
        for test in sorted(tests, key=lambda x: (x.get("category", ""), x.get("name", ""))):
            name = test.get("name", "Unknown")
            status = test.get("status", "UNKNOWN")
            category = test.get("category", "unknown")
            
            status_icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⏭️"
            f.write(f"| {name} | {status_icon} {status} | `{category}` |\n")
        
        f.write("\n")
        f.write("---\n\n")
        f.write(f"*Relatório gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")


def main():
    parser = argparse.ArgumentParser(description="Gerador de Relatórios de Testes")
    parser.add_argument("--input", required=True, help="Arquivo JSON de entrada")
    parser.add_argument("--output", required=True, help="Arquivo Markdown de saída")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  GERADOR DE RELATÓRIOS - Sistema Operacional Bom Jesus")
    print("=" * 60)
    print(f"Arquivo de entrada: {args.input}")
    print(f"Arquivo de saída: {args.output}")
    print()
    
    # Carregar resultados
    print("📥 Carregando resultados dos testes...")
    tests = load_test_results(args.input)
    print(f"   {len(tests)} testes encontrados")
    
    # Gerar relatório
    print("📝 Gerando relatório Markdown...")
    generate_markdown_report(tests, args.output)
    print(f"✅ Relatório gerado: {args.output}")
    
    # Estatísticas rápidas
    passed = sum(1 for t in tests if t.get("status") == "PASSED")
    failed = sum(1 for t in tests if t.get("status") == "FAILED")
    
    print()
    print("=" * 60)
    print("  RESUMO")
    print("=" * 60)
    print(f"Total: {len(tests)}")
    print(f"✅ Passaram: {passed}")
    print(f"❌ Falharam: {failed}")
    print()
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

