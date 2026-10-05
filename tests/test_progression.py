from plat.progression import idp

def test_idp_renders_and_blocks_prod():
    ok = idp({"application": "billing", "environment": "dev", "region": "us-central1", "scaling": 2})
    bad = idp({"application": "billing", "environment": "prod"})
    assert "google_project" in ok["terraform"]
    assert ok["applied"] is False
    assert bad["passed"] is False

