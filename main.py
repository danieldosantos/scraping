import json
import pandas as pd
from itertools import product
from playwright.sync_api import sync_playwright

dados = []

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto("https://www.fabricadolivro.com.br/imprimir-livros2/26887", timeout=60000)

    pagina.wait_for_selector("h1", timeout=15000)
    nome_produto = pagina.locator("h1").nth(0).inner_text()

    # Seletores dos grupos de opções
    grupos = pagina.query_selector_all('[class*="MuiFormGroup-root"]')
    opcoes_por_grupo = []
    for grupo in grupos:
        opcoes = grupo.query_selector_all('label')
        opcoes_por_grupo.append(opcoes)

    # Combinações de opções
    todas_combinacoes = list(product(*opcoes_por_grupo))

    for combinacao in todas_combinacoes:
        for opcao in combinacao:
            opcao.click()
            pagina.wait_for_timeout(300)

        # Aguarda atualização de preço
        pagina.wait_for_timeout(1000)

        # Coleta o preço total e unitário
        try:
            preco_total = pagina.locator('text=VALOR TOTAL').nth(0).element_handle().evaluate("e => e.nextElementSibling.innerText")
            preco_unitario = pagina.locator('text=VALOR UNITÁRIO').nth(0).element_handle().evaluate("e => e.nextElementSibling.innerText")
        except:
            preco_total = "?"
            preco_unitario = "?"

        # Coleta os campos do resumo
        resumo_dados = {}
        campos_resumo = pagina.query_selector_all("#Resumo div div")
        for i in range(0, len(campos_resumo)-1, 2):
            chave = campos_resumo[i].inner_text().strip().replace(":", "")
            valor = campos_resumo[i+1].inner_text().strip()
            resumo_dados[chave] = valor

        # Coleta os nomes das variações da combinação atual
        variacoes = [opcao.inner_text().strip() for opcao in combinacao]

        dados.append({
            "Produto": nome_produto,
            "Preço Total": preco_total,
            "Preço Unitário": preco_unitario,
            "Variações": variacoes,
            "Resumo": resumo_dados
        })

        # Reseta as seleções clicadas (opcional, dependendo da lógica do site)
        for opcao in combinacao:
            opcao.click()
            pagina.wait_for_timeout(200)

    navegador.close()

# Estrutura para Excel
linhas_excel = []
for item in dados:
    linha = {
        "Produto": item["Produto"],
        "Preço Total": item["Preço Total"],
        "Preço Unitário": item["Preço Unitário"],
    }
    for i, v in enumerate(item["Variações"]):
        linha[f"Variação {i+1}"] = v
    for k, v in item["Resumo"].items():
        linha[k] = v
    linhas_excel.append(linha)

# Salvar em Excel
df = pd.DataFrame(linhas_excel)
df.to_excel("livro2_variacoes_completas.xlsx", index=False)

# Salvar em JSON
with open("livro2_variacoes_completas.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

print("✅ Extração concluída com sucesso.")
