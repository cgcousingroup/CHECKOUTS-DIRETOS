from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API online 🚀"})

@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    data = request.json
    link_id = data.get("link_id")

    if not link_id:
        return jsonify({"erro": "link_id ausente"}), 400

    url = f"https://app.syncpayments.com.br/payment-link/{link_id}"
    print(f"Acessando: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # Preenche dados falsos obrigatórios
            page.fill('input[name="clientName"]', "Cliente Teste")
            page.fill('input[name="clientEmail"]', "teste@example.com")
            page.fill('input[name="clientCpf"]', "123.456.789-09")

            # Clica no botão de gerar QR Code
            page.click("button.sc-a13bbfcf-0.dmUMuK")

            # Espera o campo do código Pix aparecer
            page.wait_for_selector('input.sc-7620743a-4.jMaHJs', timeout=30000)
            pix_code = page.input_value('input.sc-7620743a-4.jMaHJs')

            browser.close()

        return jsonify({"pix_code": pix_code})

    except Exception as e:
        print(f"Erro Playwright: {e}")
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
