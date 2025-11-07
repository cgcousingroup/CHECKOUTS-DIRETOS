from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "API de geração de PIX online 🚀"

@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    data = request.get_json()
    link_id = data.get("link_id")

    if not link_id:
        return jsonify({"success": False, "error": "link_id obrigatório"}), 400

    link_sync = f"https://app.syncpayments.com.br/payment-link/{link_id}"

    try:
        # Faz a requisição GET
        response = requests.get(link_sync, timeout=30)
        response.raise_for_status()

        # Parseia o HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Exemplo: pegar o input que contém o código PIX
        # ATENÇÃO: seletores podem mudar dependendo do HTML
        pix_input = soup.select_one("input.sc-7620743a-4.jMaHJs")
        if not pix_input or not pix_input.get("value"):
            return jsonify({"success": False, "error": "Não foi possível encontrar o PIX no HTML"}), 400

        pix_code = pix_input["value"]

        return jsonify({"success": True, "pix_code": pix_code})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Erro na requisição: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
