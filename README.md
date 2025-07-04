# scraping

This repository contains a script that extracts variations and prices from the website [FabricadoLivro](https://www.fabricadolivro.com.br/livro2) using Playwright. The results are saved in Excel and JSON formats.

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

4. **Run the script** to generate `livro2_variacoes.xlsx` and `livro2_variacoes.json`:

   ```bash
   python main.py
   ```
