from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

app = Flask(__name__)
CORS(app)

# === Função principal que faz o scrap ===
async def obter_pix_syncpay(link_syncpay: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()
        await page.goto(link_syncpay, wait_until="networkidle")

        # Espera o elemento do QR Code aparecer
        try:
            await page.wait_for_selector("img[src^='data:image/png;base64,']", timeout=15000)
            qr_img = await page.query_selector("img[src^='data:image/png;base64,']")
            qr_code_base64 = await qr_img.get_attribute("src")
        except PlaywrightTimeout:
            qr_code_base64 = None

        # === Captura o PIX dentro da classe que você mencionou ===
        try:
            await page.wait_for_selector(".sc-7620743a-4.jMaHJs", timeout=15000)
            pix_element = await page.query_selector(".sc-7620743a-4.jMaHJs")
            pix_code = await pix_element.inner_text()
        except PlaywrightTimeout:
            pix_code = None

        # Fecha tudo
        await browser.close()

        # Verificação final
        if not pix_code:
            print("❌ Não foi possível capturar o código Pix na classe informada.")
            return None

        return {
            "pix_code": pix_code.strip(),
            "qrcode_base64": qr_code_base64
        }


@app.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    data = request.get_json()
    link_id = data.get("link_id")

    if not link_id:
        return jsonify({"success": False, "error": "link_id não informado"}), 400

    link_syncpay = f"https://syncpay.com/pay/{link_id}"
    print(f"🔗 Acessando {link_syncpay}")

    try:
        resultado = asyncio.run(obter_pix_syncpay(link_syncpay))
        if not resultado:
            return jsonify({
                "success": False,
                "error": "Não foi possível obter pix_code da SyncPayments."
            }), 500

        print("✅ PIX capturado com sucesso!")
        return jsonify({"success": True, **resultado})

    except Exception as e:
        print("❌ Erro geral:", e)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"status": "Servidor SyncPay ativo 🚀"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
