from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import threading
import subprocess
import datetime

app = Flask(__name__)
CORS(app)
lock = threading.Lock()

# === Carrega JSON na memória ===
with open("pix.json", "r", encoding="utf-8") as f:
    pix_data = json.load(f)


def git_push():
    """Executa git add, commit e push de forma assíncrona"""
    try:
        msg = f"Atualização automática {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "add", "pix.json"], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ pix.json enviado ao GitHub com sucesso!")
    except subprocess.CalledProcessError as e:
        print("⚠️ Erro ao enviar para o GitHub:", e)
    except Exception as e:
        print("⚠️ Erro inesperado:", e)


@app.route("/gerar_pix/<float:valor>", methods=["GET"])
def gerar_pix(valor):
    with lock:
        if "codigos" not in pix_data or not isinstance(pix_data["codigos"], list):
            return jsonify({"error": "Formato inválido em pix.json"}), 500

        for i, item in enumerate(pix_data["codigos"]):
            try:
                if float(item["valor"]) == float(valor):
                    codigo = item["codigo"]

                    # Remove o PIX usado
                    pix_data["codigos"].pop(i)

                    # Atualiza o arquivo JSON local
                    with open("pix.json", "w", encoding="utf-8") as f:
                        json.dump(pix_data, f, indent=2, ensure_ascii=False)

                    # Faz o push no Git (em segundo plano)
                    threading.Thread(target=git_push).start()

                    return jsonify({"copia_cola": codigo})
            except (ValueError, TypeError):
                continue

        return jsonify({"error": "Nenhum PIX disponível"}), 404


@app.route("/status", methods=["GET"])
def status():
    contagem = {}
    if "codigos" in pix_data and isinstance(pix_data["codigos"], list):
        for item in pix_data["codigos"]:
            v = float(item.get("valor", 0))
            contagem[v] = contagem.get(v, 0) + 1
    return jsonify(contagem)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
