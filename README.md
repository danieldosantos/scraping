# scraping

This repository contains a script that extracts all product variations and prices from a fixed page on [FabricadoLivro](https://www.fabricadolivro.com.br/livro2) using Playwright. The results are saved in `livro2_variacoes_completas.xlsx` and `livro2_variacoes_completas.json`.

## Setup and usage

1. **Create a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:

   ```bash
   playwright install
   ```

4. **Run the script** to generate `livro2_variacoes_completas.xlsx` and `livro2_variacoes_completas.json`:

   ```bash
   python main.py
   ```

   To see the browser while scraping, run:

   ```bash
   HEADLESS=0 python main.py
   ```
