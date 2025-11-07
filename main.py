from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import traceback
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"status": "API online 🚀"})

@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    try:
        data = request.get_json()
        link_id = data.get("link_id")

        if not link_id:
            return jsonify({"success": False, "error": "link_id obrigatório"}), 400

        link_sync = f"https://app.syncpayments.com.br/payment-link/{link_id}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print("Acessando:", link_sync)
            page.goto(link_sync, wait_until="networkidle")

            # Espera os inputs aparecerem
            page.wait_for_selector("input[name='clientName']", timeout=60000)
            page.wait_for_selector("input[name='clientEmail']", timeout=60000)
            page.wait_for_selector("input[name='clientCpf']", timeout=60000)

            # Preenche os dados
            page.fill("input[name='clientName']", "João da Silva")
            page.fill("input[name='clientEmail']", "teste@example.com")
            page.fill("input[name='clientCpf']", "12345678909")

            # Clica no botão "Gerar QR Code"
            page.wait_for_selector("button.sc-a13bbfcf-0.dmUMuK", timeout=60000)
            page.click("button.sc-a13bbfcf-0.dmUMuK")

            # Espera o campo com o código Pix aparecer
            page.wait_for_selector("input.sc-7620743a-4.jMaHJs", timeout=60000)

            # Pega o valor do campo (é o código PIX)
            pix_code = page.get_attribute("input.sc-7620743a-4.jMaHJs", "value")

            browser.close()

            if not pix_code:
                return jsonify({"success": False, "error": "Campo de PIX encontrado, mas sem valor."}), 400

            return jsonify({"success": True, "pix_code": pix_code})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway define a porta
    app.run(host="0.0.0.0", port=port)

