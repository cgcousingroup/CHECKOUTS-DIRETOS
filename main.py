import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

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
        valor = data.get("valor")  # caso queira passar valor também

        if not link_id:
            return jsonify({"success": False, "error": "link_id obrigatório"}), 400

        # 🔹 MOCK do Pix
        # Substitua depois pelo seu Playwright real ou outro método
        pix_code = f"PIX-CODIGO-DE-TEXTO-{link_id}"

        return jsonify({"success": True, "pix_code": pix_code})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # ⚠️ Railway fornece a porta via variável de ambiente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
