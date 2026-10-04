# Self-Service Internal Developer Platform

Phase 6-7

Skills: templates, RBAC-shaped env, Terraform/Helm/Argo plan, audit

Portal request → FastAPI → render Terraform/Helm/Argo files. prod and latest fail. applied false.

```bash
pip install -r requirements.txt
pytest -q
```

Laptop proof. No hosted model. Cluster apply stays false until a human approves.
