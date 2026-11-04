import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

DIR_CSVS = Path("/opt/projeto/csvs")
ARQUIVOS_PROCESSADOS = Path("/opt/projeto/etl/arquivos_processados.txt")
ARQUIVOS_ESPERADOS = 6
URL_ORIGEM = "http://192.168.122.10:8000/"

def main():
    if not DIR_CSVS.exists():
        print(f"Erro: Diretório {DIR_CSVS} não existe.")
        sys.exit(1)

    ARQUIVOS_PROCESSADOS.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PATH"] = (
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
        + env.get("PATH", "")
    )

    print("Buscando novos CSVs na VM 1...")
    wget_bin = shutil.which("wget", path=env["PATH"]) or "/usr/bin/wget"

    cmd_wget = [
        wget_bin,
        "--no-clobber",
        "--recursive",
        "--no-parent",
        "--no-directories",
        "-accept=csv",
        f"--directory-prefix={str(DIR_CSVS)}",
        URL_ORIGEM,
    ]
    subprocess.run(cmd_wget, env=env, check=False)

    processed_files = set()
    if ARQUIVOS_PROCESSADOS.exists():
        processed_files = set(
            line.strip()
            for line in ARQUIVOS_PROCESSADOS.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        )

    # agrupa por id do lote
    lotes = defaultdict(list)
    for csv_file in DIR_CSVS.glob("*.csv"):
        if csv_file.name not in processed_files:
            # Extrai o ID do lote antes do primeiro hífen '-'
            lote_id = csv_file.name.split("-")[0]
            lotes[lote_id].append(csv_file)

    rscript_bin = (
        shutil.which("Rscript", path=env["PATH"]) or "/usr/bin/Rscript"
    )

    # executa o script, um lote por vez, apenas em lotes completos
    for lote_id, files in lotes.items():
        if len(files) == ARQUIVOS_ESPERADOS:
            files_sorted = sorted(files, key=lambda f: f.name)

            print(
                f"Lote {lote_id} completo"
                f" ({ARQUIVOS_ESPERADOS}/{ARQUIVOS_ESPERADOS}). Executando"
                " R..."
            )

            cmd = [
                rscript_bin,
                "/opt/projeto/etl/clean_data.R",
                lote_id,
            ] + [str(f) for f in files_sorted]

            result = subprocess.run(cmd, env=env)

            if result.returncode == 0:
                with open(ARQUIVOS_PROCESSADOS, "a", encoding="utf-8") as f:
                    for f_path in files_sorted:
                        f.write(f"{f_path.name}\n")
                print(f"Lote {lote_id} registrado com sucesso.")
            else:
                print(
                    f"Erro ao processar lote {lote_id}. Interrompendo"
                    " execução."
                )
                sys.exit(1)


if __name__ == "__main__":
    main()