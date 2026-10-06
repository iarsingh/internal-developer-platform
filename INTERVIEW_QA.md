# internal-developer-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does internal-developer-platform address, and what can you demonstrate?

Portal request → FastAPI → render Terraform/Helm/Argo files. prod and latest fail. applied false.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/plat/main.py`](src/plat/main.py): Implementation or supporting configuration.
- [`src/plat/ops.py`](src/plat/ops.py): Implementation or supporting configuration.
- [`src/plat/gate.py`](src/plat/gate.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`terraform/main.tf`](terraform/main.tf): Terraform resource/module declarations.
- [`web/src/App.tsx`](web/src/App.tsx): User interface code/assets.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `check` and explain the decision it makes?

The main walkthrough here is `check(body, approved=False)` in [`src/plat/gate.py`](src/plat/gate.py#L1).

```python
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
```

The implementation calls `body.get`, `bool`, `failed.append`, `image.endswith`, `str`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=404, detail='workspace not found')` in [`src/plat/ops.py`](src/plat/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/plat/ops.py`](src/plat/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/plat/ops.py`](src/plat/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/plat/ops.py`](src/plat/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_gate.py`](tests/test_gate.py#L5) contains `test_pass_fail`:

```python
def test_pass_fail():
    assert client.post("/check", json={'env': 'dev', 'template': 'python-service', 'owner': 'ada', 'image': 'api:1.2.3'}).json()["passed"] is True
    bad = client.post("/check", json={'env': 'prod', 'template': 'python-service', 'owner': 'ada', 'image': 'api:1.2.3'}).json()
    assert bad["passed"] is False
    assert "env" in bad["failed"]
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/plat/main.py`](src/plat/main.py#L8).
- `POST /check` → `post_check` in [`src/plat/main.py`](src/plat/main.py#L12).
- `GET /readyz` → `readyz` in [`src/plat/ops.py`](src/plat/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/plat/ops.py`](src/plat/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/plat/ops.py`](src/plat/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/plat/ops.py`](src/plat/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/plat/ops.py`](src/plat/ops.py#L130).
- `POST /jobs/{job_id}/approve` → `approve_job` in [`src/plat/ops.py`](src/plat/ops.py#L140).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. Where does state live, and what happens with multiple workers?

Module-level containers include `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/plat/ops.py`](src/plat/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `check`?

In [`src/plat/gate.py`](src/plat/gate.py#L1), `check(body, approved=False)` receives the inputs. The function computes these intermediate values:

- `failed = []`
- `image = str(body.get('image', ''))`
- `env = body.get('env')`

Its result is defined by:

- `{'passed': not failed, 'failed': failed, 'applied': False, 'approved': bool(approved)}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/plat/gate.py`](src/plat/gate.py#L1) branches on:

- `image.endswith(':latest') or image == 'latest'`
- `env not in {'dev', 'staging'}`
- `not body.get('template')`
- `not body.get('owner')`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 13. What does `web/src/App.tsx` own?

[`web/src/App.tsx`](web/src/App.tsx) defines `App`.

Trace these definitions and imports to explain the module boundary. Relative imports identify project code; package imports should be checked against the nearest manifest.

## 14. What does the operations plane add, and where is its limit?

[`src/plat/ops.py`](src/plat/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
