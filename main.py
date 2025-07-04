import json
import pandas as pd
from itertools import product
from playwright.sync_api import sync_playwright

dados = []

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto("https://www.fabricadolivro.com.br/livro2", timeout=60000)

    pagina.wait_for_selector("h1", timeout=15000)
    nome_produto = pagina.locator("h1").nth(0).inner_text()

    grupos = pagina.query_selector_all('[class*="MuiFormGroup-root"]')
    opcoes_por_grupo = []
    for grupo in grupos:
        opcoes = grupo.query_selector_all('label')
        nomes_opcoes = [op.inner_text().strip() for op in opcoes]
        opcoes_por_grupo.append((grupo, opcoes, nomes_opcoes))

    todas_combinacoes = list(product(*[g[1] for g in opcoes_por_grupo]))
    preco_locator = pagina.locator('[data-testid="price"]')

    for combinacao in todas_combinacoes:
        preco_anterior = preco_locator.inner_text().strip()

        for opcao in combinacao:
            opcao.click()
            pagina.wait_for_timeout(300)

        pagina.wait_for_function(
            "(prev) => document.querySelector('[data-testid=\"price\"]').innerText.trim() !== prev",
            preco_anterior,
        )

        preco = preco_locator.inner_text().strip()
        variacoes = [opcao.inner_text().strip() for opcao in combinacao]

        dados.append({
            "Produto": nome_produto,
            "Preço": preco,
            "Variações": variacoes
        })

        for opcao in combinacao:
            opcao.click()
            pagina.wait_for_timeout(300)

    navegador.close()

# Salvar Excel
linhas_excel = []
for item in dados:
    linha = {"Produto": item["Produto"], "Preço": item["Preço"]}
    for i, v in enumerate(item["Variações"]):
        linha[f"Variação {i+1}"] = v
    linhas_excel.append(linha)

df = pd.DataFrame(linhas_excel)
df.to_excel("livro2_variacoes.xlsx", index=False)

# Salvar JSON
with open("livro2_variacoes.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

print("✅ Extração concluída com sucesso.")
