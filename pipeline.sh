#!/usr/bin/bash

# Este script:
# 1. Baixa os novos CSVs da VM do gerador
# 2. Executa o processo de limpeza neles
# 3. Provê os arquivos para download na máquina local

cd /opt/projeto/csvs || exit

# Baixar arquivos
wget --recursive \
    --no-directories \
    --no-parent \
    --no-clobber \
    --accept=csv \
    http://192.168.122.10:8000
