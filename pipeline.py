import os
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

DIR_CSVS = Path("/opt/projeto/csvs")
DIR_PROCESSADOS = Path("/opt/projeto/processados")
SCRIPT_R = Path("/opt/projeto/etl/etl-script.R")
ARQUIVOS_ESPERADOS = 6
INTERVALO_POLLING = 3  # Segundos entre cada checagem


def main():
    DIR_CSVS.mkdir(parents=True, exist_ok=True)
    DIR_PROCESSADOS.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PATH"] = (
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
        + env.get("PATH", "")
    )

    rscript_bin = (
        shutil.which("Rscript", path=env["PATH"]) or "/usr/bin/Rscript"
    )

    print(f"Iniciando daemon do orquestrador. Monitorando {DIR_CSVS}...")

    while True:
        try:
            # agrupa por id do lote
            lotes = defaultdict(list)
            for csv_file in DIR_CSVS.glob("*.csv"):
                # Ignora arquivos temporarios de transferencia
                if csv_file.name.startswith("."):
                    continue

                # Extrai o ID do lote antes do primeiro hífen '-'
                lote_id = csv_file.name.split("-")[0]
                lotes[lote_id].append(csv_file)

            # executa o script, um lote por vez, apenas em lotes completos
            for lote_id, files in list(lotes.items()):
                if len(files) == ARQUIVOS_ESPERADOS:
                    files_sorted = sorted(files, key=lambda f: f.name)

                    print(
                        f"Lote {lote_id} completo"
                        f" ({ARQUIVOS_ESPERADOS}/{ARQUIVOS_ESPERADOS})."
                        " Executando R..."
                    )

                    cmd = [
                        rscript_bin,
                        str(SCRIPT_R),
                        lote_id,
                    ] + [str(f) for f in files_sorted]

                    result = subprocess.run(cmd, env=env)

                    if result.returncode == 0:
                        # Move os arquivos processados para a pasta final (limpa a fila)
                        for f_path in files_sorted:
                            shutil.move(
                                str(f_path), str(DIR_PROCESSADOS / f_path.name)
                            )
                        print(
                            f"Lote {lote_id} processado e movido para"
                            f" {DIR_PROCESSADOS} com sucesso."
                        )
                    else:
                        print(
                            f"Erro ao processar lote {lote_id}. Arquivos"
                            " mantidos na fila."
                        )

        except Exception as e:
            print(f"Erro inesperado no loop do daemon: {e}")

        time.sleep(INTERVALO_POLLING)


if __name__ == "__main__":
    main()