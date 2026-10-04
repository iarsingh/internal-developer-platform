def check(body, approved=False):
    failed = []

    image = str(body.get("image", ""))
    if image.endswith(":latest") or image == "latest":
        failed.append("latest")

    env = body.get("env");
    if env not in {"dev", "staging"}: failed.append("env")
    if not body.get("template"): failed.append("template")
    if not body.get("owner"): failed.append("owner")
    return {"passed": not failed, "failed": failed, "applied": False, "approved": bool(approved)}
