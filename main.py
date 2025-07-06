import json
import os
from itertools import product

import pandas as pd
from playwright.sync_api import TimeoutError, sync_playwright


def scrape(url: str, headless: bool = True):
    """Extrai as variações do produto e retorna uma lista de dicionários."""

    dados = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=headless)
        pagina = navegador.new_page()
        pagina.goto(url, timeout=60_000, wait_until="domcontentloaded")

        pagina.wait_for_selector("h1", timeout=15_000)
        nome_produto = pagina.locator("h1").nth(0).inner_text()

        grupos = pagina.query_selector_all('[class*="MuiFormGroup-root"]')
        opcoes_por_grupo = [g.query_selector_all("label") for g in grupos]

        todas_combinacoes = list(product(*opcoes_por_grupo))

        for combinacao in todas_combinacoes:
            for opcao in combinacao:
                opcao.click()
                pagina.wait_for_timeout(300)

            pagina.wait_for_timeout(1_000)

            try:
                preco_total = (
                    pagina.locator("text=/VALOR TOTAL/i")
                    .nth(0)
                    .evaluate("e => e.nextElementSibling.innerText")
                )
                preco_unitario = (
                    pagina.locator("text=/VALOR UNIT\xc3\x81RIO/i")
                    .nth(0)
                    .evaluate("e => e.nextElementSibling.innerText")
                )
            except TimeoutError:
                preco_total = "?"
                preco_unitario = "?"

            resumo_dados = {}
            campos_resumo = pagina.query_selector_all("#Resumo div div")
            for i in range(0, len(campos_resumo) - 1, 2):
                chave = campos_resumo[i].inner_text().strip().replace(":", "")
                valor = campos_resumo[i + 1].inner_text().strip()
                resumo_dados[chave] = valor

            variacoes = [op.inner_text().strip() for op in combinacao]

            dados.append(
                {
                    "Produto": nome_produto,
                    "Preço Total": preco_total,
                    "Preço Unitário": preco_unitario,
                    "Variações": variacoes,
                    "Resumo": resumo_dados,
                }
            )

            for opcao in combinacao:
                opcao.click()
                pagina.wait_for_timeout(200)

        navegador.close()

    return dados


if __name__ == "__main__":
    headless = os.getenv("HEADLESS", "1") != "0"
    url = "https://www.fabricadolivro.com.br/imprimir-livros2/26887"
    dados = scrape(url=url, headless=headless)

    linhas_excel = []
    for item in dados:
        linha = {
            "Produto": item["Produto"],
            "Preço Total": item["Preço Total"],
            "Preço Unitário": item["Preço Unitário"],
        }
        for i, v in enumerate(item["Variações"]):
            linha[f"Variação {i + 1}"] = v
        for k, v in item["Resumo"].items():
            linha[k] = v
        linhas_excel.append(linha)

    df = pd.DataFrame(linhas_excel)
    df.to_excel("livro2_variacoes_completas.xlsx", index=False)

    with open("livro2_variacoes_completas.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    print("✅ Extração concluída com sucesso.")
