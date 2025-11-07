from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import traceback

app = Flask(__name__)
CORS(app)

@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    try:
        data = request.get_json()
        link_id = data.get("link_id")

        if not link_id:
            return jsonify({"success": False, "error": "link_id obrigatório"}), 400

        # URL do pagamento Sync
        link_sync = f"https://app.syncpayments.com.br/payment-link/{link_id}"
        session = requests.Session()

        # Cabeçalhos básicos para simular navegador
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }

        # 1️⃣ Pega o HTML da página inicial
        resp = session.get(link_sync, headers=headers, timeout=30)
        if resp.status_code != 200:
            return jsonify({"success": False, "error": "Não foi possível acessar o link Sync"}), 400

        soup = BeautifulSoup(resp.text, "html.parser")

        # 2️⃣ Extrai o token hidden se houver (ex: CSRF ou outros)
        # Exemplo:
        csrf_token = ""
        token_input = soup.find("input", {"name": "csrfToken"})
        if token_input:
            csrf_token = token_input.get("value", "")

        # 3️⃣ Monta payload para envio dos dados do cliente
        payload = {
            "clientName": "João da Silva",
            "clientEmail": "teste@example.com",
            "clientCpf": "12345678909",
        }
        if csrf_token:
            payload["csrfToken"] = csrf_token

        # 4️⃣ Envia POST simulando clique no botão "Gerar QR Code"
        post_headers = headers.copy()
        post_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
        })

        post_resp = session.post(link_sync, headers=post_headers, data=payload, timeout=30)
        if post_resp.status_code != 200:
            return jsonify({"success": False, "error": "Erro ao enviar os dados do cliente"}), 400

        # 5️⃣ Pega o HTML final e extrai o código PIX
        final_soup = BeautifulSoup(post_resp.text, "html.parser")
        pix_input = final_soup.find("input", {"class": "sc-7620743a-4 jMaHJs"})

        if not pix_input or not pix_input.get("value"):
            return jsonify({"success": False, "error": "Não foi possível encontrar o PIX no HTML"}), 400

        pix_code = pix_input["value"]

        return jsonify({"success": True, "pix_code": pix_code})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
