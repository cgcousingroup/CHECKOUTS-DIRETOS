from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import threading

app = Flask(__name__)
CORS(app)  # permite requisições de qualquer origem
lock = threading.Lock()  # evita concorrência

# === Carrega JSON na memória ===
with open("pix.json", "r", encoding="utf-8") as f:
    pix_data = json.load(f)

@app.route("/gerar_pix/<float:valor>", methods=["GET"])
def gerar_pix(valor):
    with lock:
        # percorre cada bloco dentro da lista principal
        for bloco in pix_data:
            if "codigos" in bloco and isinstance(bloco["codigos"], list):
                for i, item in enumerate(bloco["codigos"]):
                    try:
                        # garante que valor é comparado como float
                        if float(item["valor"]) == float(valor):
                            codigo = item["codigo"]
                            # remove o item usado
                            bloco["codigos"].pop(i)
                            # salva novamente no arquivo JSON
                            with open("pix.json", "w", encoding="utf-8") as f:
                                json.dump(pix_data, f, indent=2, ensure_ascii=False)
                            return jsonify({"copia_cola": codigo})
                    except (ValueError, TypeError):
                        continue
        # se não encontrar PIX do valor pedido
        return jsonify({"error": "Nenhum PIX disponível"}), 404

# === Endpoint opcional: mostra quantos PIX restam por valor ===
@app.route("/status", methods=["GET"])
def status():
    contagem = {}
    for bloco in pix_data:
        if "codigos" in bloco and isinstance(bloco["codigos"], list):
            for item in bloco["codigos"]:
                v = float(item.get("valor", 0))
                contagem[v] = contagem.get(v, 0) + 1
    return jsonify(contagem)

# === Serve o frontend (index.html) ===
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# === Inicia o servidor Flask ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
