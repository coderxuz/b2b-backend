import datetime
import pytest
import time
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from main import app
from common import get_redis_client
from db.connection import async_engine


@pytest.mark.asyncio
async def test_admin_firm_and_category_crud():
    redis = get_redis_client()
    ts = int(time.time() * 1000)
    admin_phone = f"+99890{ts % 10000000:07d}"
    dist_phone = f"+99891{ts % 10000000:07d}"
    otp = "123456"

    await redis.set(f"otp:{admin_phone}", otp, ex=180)
    await redis.set(f"otp:{dist_phone}", otp, ex=180)
    await redis.aclose()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register Admin
        admin_res = await ac.post("/auth/register", json={
            "phone": admin_phone,
            "otp": otp,
            "first_name": "Admin",
            "role": "admin"
        })
        assert admin_res.status_code == 201, admin_res.text
        admin_token = admin_res.json()["access_token"]

        # 2. Register Distributor & Create Firm
        dist_res = await ac.post("/auth/register", json={
            "phone": dist_phone,
            "otp": otp,
            "first_name": "Distributor",
            "role": "distributor"
        })
        assert dist_res.status_code == 201, dist_res.text
        dist_token = dist_res.json()["access_token"]

        firm_res = await ac.post("/firm", json={"name": "Test Firm LLC"}, headers={"Authorization": f"Bearer {dist_token}"})
        assert firm_res.status_code == 201, firm_res.text
        firm_id = firm_res.json()["id"]
        assert firm_res.json()["is_active"] is True

        # 3. Admin Get All Firms with limit & offset
        list_firms_res = await ac.get(
            "/firm/admin/all?limit=5&offset=0",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert list_firms_res.status_code == 200, list_firms_res.text
        firms_data = list_firms_res.json()
        assert isinstance(firms_data, list)
        assert len(firms_data) >= 1

        # Non-admin access should be forbidden
        list_firms_dist = await ac.get(
            "/firm/admin/all?limit=5&offset=0",
            headers={"Authorization": f"Bearer {dist_token}"}
        )
        assert list_firms_dist.status_code == 403

        # 4. Admin Get Single Firm by ID
        get_firm_res = await ac.get(
            f"/firm/admin/{firm_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_firm_res.status_code == 200, get_firm_res.text
        assert get_firm_res.json()["id"] == firm_id
        assert get_firm_res.json()["name"] == "Test Firm LLC"

        # 5. Admin Deactivates Firm
        deact_res = await ac.patch(
            f"/firm/{firm_id}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert deact_res.status_code == 200, deact_res.text
        assert deact_res.json()["is_active"] is False

        # 6. Admin Category CRUD
        # Create Category
        cat_create = await ac.post(
            "/admin/categories",
            json={"name": f"Soft Drinks {ts}"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cat_create.status_code == 201, cat_create.text
        cat_id = cat_create.json()["id"]

        # List Categories
        cat_list = await ac.get(
            "/admin/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cat_list.status_code == 200
        assert len(cat_list.json()) >= 1

        # Get Category
        cat_get = await ac.get(
            f"/admin/categories/{cat_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cat_get.status_code == 200

        # Update Category
        cat_update = await ac.patch(
            f"/admin/categories/{cat_id}",
            json={"name": f"Juices & Drinks {ts}"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cat_update.status_code == 200
        assert cat_update.json()["name"] == f"Juices & Drinks {ts}"

        # Delete Category
        cat_del = await ac.delete(
            f"/admin/categories/{cat_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cat_del.status_code == 204


@pytest.mark.asyncio
async def test_account_over_9_months_raises_get_tarrif():
    redis = get_redis_client()
    ts = int(time.time() * 1000)
    phone = f"+99892{ts % 10000000:07d}"
    otp = "123456"
    await redis.set(f"otp:{phone}", otp, ex=180)
    await redis.aclose()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg_res = await ac.post("/auth/register", json={
            "phone": phone,
            "otp": otp,
            "first_name": "OldUser",
            "role": "distributor"
        })
        assert reg_res.status_code == 201
        user_id = reg_res.json()["user"]["id"]
        token = reg_res.json()["access_token"]

        # Directly update DB via connection
        ten_months_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=300)
        async with async_engine.begin() as conn:
            await conn.execute(
                text("UPDATE users SET created_at = :created_at WHERE id = :user_id"),
                {"created_at": ten_months_ago, "user_id": user_id}
            )

        # Call protected route -> should fail with 403 "get_tarrif"
        me_res = await ac.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 403
        assert me_res.json()["detail"] == "get_tarrif"

        # Try to login -> should fail with 403 "get_tarrif"
        redis = get_redis_client()
        await redis.set(f"otp:{phone}", otp, ex=180)
        await redis.aclose()

        login_res = await ac.post("/auth/login", json={"phone": phone, "otp": otp})
        assert login_res.status_code == 403
        assert login_res.json()["detail"] == "get_tarrif"
