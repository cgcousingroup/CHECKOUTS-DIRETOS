from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json, threading

app = Flask(__name__)
CORS(app)  # permite requisições de qualquer origem
lock = threading.Lock()  # evita concorrência

# Carrega JSON na memória
with open("pix.json", "r", encoding="utf-8") as f:
    pix_data = json.load(f)

@app.route("/gerar_pix/<float:valor>", methods=["GET"])
def gerar_pix(valor):
    with lock:
        for i, item in enumerate(pix_data["codigos"]):
            if item["valor"] == valor:
                codigo = item["codigo"]
                # remove do JSON para não ser reutilizado
                pix_data["codigos"].pop(i)
                # salva de volta no arquivo
                with open("pix.json", "w", encoding="utf-8") as f:
                    json.dump(pix_data, f, indent=2, ensure_ascii=False)
                return jsonify({"copia_cola": codigo})
        return jsonify({"error": "Nenhum PIX disponível"}), 404

# Serve o frontend HTML
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



