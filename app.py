from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import threading
import requests
import base64
import os

app = Flask(__name__)
CORS(app)
lock = threading.Lock()

# === Configuração do repositório GitHub ===
GITHUB_REPO = "cgcousingroup/CHECKOUTS-DIRETOS"  # exemplo: "utmify/pix-server"
GITHUB_FILE_PATH = "pix.json"         # caminho dentro do repositório
GITHUB_BRANCH = "main"                # ou "master", conforme seu repositório
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # variável de ambiente com o token

# === Carrega JSON na memória ===
with open("pix.json", "r", encoding="utf-8") as f:
    pix_data = json.load(f)


def atualizar_github():
    """Envia o pix.json atualizado para o GitHub via API."""
    try:
        # Lê o JSON local
        with open(GITHUB_FILE_PATH, "r", encoding="utf-8") as f:
            conteudo = f.read()

        # Busca o SHA atual do arquivo no GitHub
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        resp = requests.get(url, headers=headers)
        sha = resp.json().get("sha")

        # Prepara payload de atualização
        data = {
            "message": "Atualização automática via servidor Flask",
            "content": base64.b64encode(conteudo.encode("utf-8")).decode("utf-8"),
            "branch": GITHUB_BRANCH,
            "sha": sha
        }

        # Envia para o GitHub
        r = requests.put(url, headers=headers, json=data)

        if r.status_code in (200, 201):
            print("✅ pix.json atualizado no GitHub com sucesso!")
        else:
            print("⚠️ Falha ao atualizar no GitHub:", r.text)

    except Exception as e:
        print("⚠️ Erro ao enviar para o GitHub:", e)


@app.route("/gerar_pix/<float:valor>", methods=["GET"])
def gerar_pix(valor):
    with lock:
        for bloco in pix_data:
            if "codigos" in bloco and isinstance(bloco["codigos"], list):
                for i, item in enumerate(bloco["codigos"]):
                    try:
                        if float(item["valor"]) == float(valor):
                            codigo = item["codigo"]
                            bloco["codigos"].pop(i)

                            # Salva no arquivo local
                            with open("pix.json", "w", encoding="utf-8") as f:
                                json.dump(pix_data, f, indent=2, ensure_ascii=False)

                            # Atualiza no GitHub
                            threading.Thread(target=atualizar_github).start()

                            return jsonify({"copia_cola": codigo})
                    except (ValueError, TypeError):
                        continue
        return jsonify({"error": "Nenhum PIX disponível"}), 404


@app.route("/status", methods=["GET"])
def status():
    contagem = {}
    for bloco in pix_data:
        if "codigos" in bloco and isinstance(bloco["codigos"], list):
            for item in bloco["codigos"]:
                v = float(item.get("valor", 0))
                contagem[v] = contagem.get(v, 0) + 1
    return jsonify(contagem)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
