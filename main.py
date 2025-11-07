from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route("/gerar_pix", methods=["GET"])
def gerar_pix():
    try:
        data = request.get_json()
        link_id = data.get("link_id")

        if not link_id:
            return jsonify({"success": False, "error": "link_id obrigatório"}), 400

        link_sync = f"https://app.syncpayments.com.br/payment-link/{link_id}"

        # Simula o envio dos dados do cliente
        payload = {
            "clientName": "João da Silva",
            "clientEmail": "teste@example.com",
            "clientCpf": "12345678909"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # Faz o POST ou GET (dependendo de como o SyncPayments espera)
        response = requests.post(link_sync, data=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Erro ao acessar link: {response.status_code}"}), 500

        soup = BeautifulSoup(response.text, "html.parser")

        # Pega o valor do PIX pelo seletor que você já tinha
        pix_input = soup.select_one("input.sc-7620743a-4.jMaHJs")
        if not pix_input or not pix_input.get("value"):
            return jsonify({"success": False, "error": "Não foi possível encontrar o PIX no HTML"}), 400

        pix_code = pix_input.get("value")

        return jsonify({"success": True, "pix_code": pix_code})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

