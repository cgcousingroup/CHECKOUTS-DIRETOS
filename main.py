from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)  # Permite que o front na Hostinger acesse a API

# Rota raiz para testar se a API está online
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API online 🚀"})

# Rota para gerar PIX
@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    data = request.get_json()  # mais seguro que request.json
    link_id = data.get("link_id")
    valor = data.get("valor")  # caso queira usar o valor no futuro

    if not link_id:
        return jsonify({"success": False, "error": "link_id ausente"}), 400

    url = f"https://app.syncpayments.com.br/payment-link/{link_id}"
    print(f"Acessando: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # Preenche dados obrigatórios falsos
            page.fill('input[name="clientName"]', "Cliente Teste")
            page.fill('input[name="clientEmail"]', "teste@example.com")
            page.fill('input[name="clientCpf"]', "123.456.789-09")

            # Clica no botão de gerar QR Code
            page.click("button.sc-a13bbfcf-0.dmUMuK")

            # Espera o campo do código Pix aparecer
            page.wait_for_selector('input.sc-7620743a-4.jMaHJs', timeout=30000)
            pix_code = page.input_value('input.sc-7620743a-4.jMaHJs')

            browser.close()

        return jsonify({"success": True, "pix_code": pix_code})

    except Exception as e:
        print(f"Erro Playwright: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Porta padrão do Railway
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
