import pytest

@pytest.mark.asyncio
async def test_onboarding_flow(client):
    await client.post(
        "/api/guides",
        json={
            "track": "eng",
            "title": "Laptop setup",
            "body": "Install the VPN client, then request GitHub org access from IT. "
            "Clone the monorepo and run make bootstrap.",
        },
    )
    check = await client.post("/api/checklist", json={"label": "VPN installed", "track": "eng"})
    item_id = check.json()["id"]
    toggled = await client.post(f"/api/checklist/{item_id}/toggle")
    assert toggled.json()["done"] is True
    ask = await client.post(
        "/api/ask", json={"question": "How do I get GitHub access?", "track": "eng"}
    )
    assert ask.status_code == 200
    assert ask.json()["citations"]
