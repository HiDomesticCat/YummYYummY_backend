import secrets
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional

# 建立 FastAPI 應用實例
app = FastAPI()

# 為了 PoC，我們使用一個簡單的字典在記憶體中暫存 Nonce。
nonce_storage = {}

# --- API 端點定義 ---

@app.get("/health", tags=["System"])
async def health_check():
    """
    提供一個簡單的健康檢查端點，供 App 確認後端服務是否在線。
    """
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/v1/capture/initiate", tags=["Capture"])
async def initiate_capture():
    """
    產生一個結構化的 WebAuthn 挑戰物件。
    """
    challenge = secrets.token_urlsafe(32)
    expiry_time = time.time() + 300 # 5 分鐘過期
    nonce_storage[challenge] = expiry_time

    print(f"產生的挑戰 (Nonce): {challenge}")

    # 建立並回傳一個結構化的 WebAuthn 挑戰物件
    webauthn_challenge = {
        "challenge": challenge,
        "rp": {
            # 【重要】這個域名在部署後需要修改
            "id": "your-service-name.onrender.com", 
            "name": "SpectraLens PoC"
        },
        "user": {
            "id": "mock_user_id_123",
            "name": "poc_user@example.com",
            "displayName": "PoC User"
        },
        "pubKeyCredParams": [
            {"type": "public-key", "alg": -7}, # ES256
            {"type": "public-key", "alg": -257} # RS256
        ],
        "timeout": 60000,
        "attestation": "none"
    }

    return webauthn_challenge


@app.post("/api/v1/capture/submit", tags=["Capture"])
async def submit_capture(
    photo: UploadFile = File(..., description="使用者拍攝的照片檔案"),
    pHash: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    isMocked: bool = Form(...),
    passkeyResponse: str = Form(...),
    integrityToken: str = Form(...),
    clientTimestamp: str = Form(...),
    dataVersion: Optional[str] = Form(None)
):
    """
    接收所有數據，執行模擬驗證，並回傳 App 期望的格式。
    """
    print("收到提交請求：")
    print(f"  - pHash: {pHash}")
    print(f"  - 照片檔案名稱: {photo.filename}")

    # === 模擬後端驗證流程 ===
    # 在真實應用中，您會在這裡呼叫 Google API 和密碼學函式庫進行真實驗證。

    print("模擬 Play Integrity 令牌檢查...")
    print("✅ Play Integrity 令牌存在性檢查成功。")

    print("模擬 Passkey 回應簽名檢查...")
    print("✅ Passkey 回應存在性檢查成功。")

    print("✅ 所有模擬驗證通過！數據被視為可信。")

    # 回傳 App 期望的成功格式
    return {"success": True, "message": "數據已成功驗證並儲存。"}