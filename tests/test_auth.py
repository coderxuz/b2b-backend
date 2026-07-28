import pytest
import time
from httpx import AsyncClient, ASGITransport
from main import app
from common import get_redis_client


@pytest.mark.asyncio
async def test_auth_and_firm_flow():
    # 1. Store OTP directly in Redis with unique test phone
    redis = get_redis_client()
    phone = f"+99890{int(time.time()) % 10000000:07d}"
    otp = "123456"
    await redis.set(f"otp:{phone}", otp, ex=180)
    await redis.aclose()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 2. Register user
        reg_payload = {
            "phone": phone,
            "otp": otp,
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "role": "distributor"
        }
        res = await ac.post("/auth/register", json=reg_payload)
        assert res.status_code == 201, res.text
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["phone"] == phone
        assert data["user"]["firm"] is None

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        # 3. Get profile (/auth/me)
        me_res = await ac.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["phone"] == phone

        # 4. Create firm for logged in distributor
        firm_payload = {
            "name": "Best Wholesale LLC",
            "inn": "123456789",
            "mfo": "00123",
            "address": "Tashkent, Chilanzar 5",
            "location": "41.311081, 69.240562",
            "firm_category": "Drink Wholesale",
            "description": "Leading distributor of soft drinks",
            "additional_phones": ["+998901234568"]
        }
        firm_res = await ac.post("/firm", json=firm_payload, headers={"Authorization": f"Bearer {access_token}"})
        assert firm_res.status_code == 201, firm_res.text
        firm_data = firm_res.json()
        assert firm_data["name"] == "Best Wholesale LLC"
        assert firm_data["inn"] == "123456789"

        # 5. Get my firm (/firm/me)
        my_firm_res = await ac.get("/firm/me", headers={"Authorization": f"Bearer {access_token}"})
        assert my_firm_res.status_code == 200
        assert my_firm_res.json()["name"] == "Best Wholesale LLC"

        # 6. Test Refresh Token
        ref_res = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert ref_res.status_code == 200
        assert "access_token" in ref_res.json()

        # 7. Test Login
        redis = get_redis_client()
        await redis.set(f"otp:{phone}", otp, ex=180)
        await redis.aclose()

        login_res = await ac.post("/auth/login", json={"phone": phone, "otp": otp})
        assert login_res.status_code == 200
        assert login_res.json()["user"]["firm"]["name"] == "Best Wholesale LLC"
