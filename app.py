from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import re
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

# Função assíncrona que faz o scraping da SyncPay
async def obter_pix_syncpay(link_syncpay: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()
        await page.goto(link_syncpay, wait_until="networkidle")

        # Espera o QR Code aparecer
        await page.wait_for_selector("img[src^='data:image/png;base64,']", timeout=15000)
        qr_img = await page.query_selector("img[src^='data:image/png;base64,']")
        qr_code_base64 = await qr_img.get_attribute("src")

        # Extrai o código Pix (copia e cola)
        html = await page.content()
        match = re.search(r"0002010102.*?6304[0-9A-Fa-f]{4}", html)
        pix_code = match.group(0) if match else None

        await browser.close()

        if not pix_code or not qr_code_base64:
            return None
        return {"pix_code": pix_code, "qrcode_base64": qr_code_base64}


@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    """Recebe link_id e valor do front, gera o QR da SyncPay e retorna JSON."""
    data = request.get_json()
    link_id = data.get("link_id")
    valor = data.get("valor")

    if not link_id:
        return jsonify({"success": False, "error": "link_id não informado"}), 400

    link_syncpay = f"https://syncpay.com/pay/{link_id}"
    print(f"🔗 Gerando PIX via {link_syncpay}")

    try:
        resultado = asyncio.run(obter_pix_syncpay(link_syncpay))
        if not resultado:
            return jsonify({"success": False, "error": "Não foi possível obter PIX da SyncPay"}), 500

        print("✅ PIX gerado com sucesso!")
        return jsonify({"success": True, **resultado})

    except Exception as e:
        print("❌ Erro:", e)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"status": "Servidor SyncPay ativo 🚀"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
