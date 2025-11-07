#!/bin/bash

# Instala o Chromium necessário para o Playwright
playwright install chromium

# Inicia a aplicação Flask
python main.py
