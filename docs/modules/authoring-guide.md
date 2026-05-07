# Module Authoring Guide

A Nexus OSINT module is a self-contained Python class that:
1. Declares its legal/T&S metadata
2. Accepts an input entity
3. Returns a list of entities and relationships to add to the graph

---

## The Graph Model

Everything in Nexus OSINT is either an **Entity** or a **Relationship**.

**Entity** — a node in the graph:
```
id            unique string (use a hash of the canonical value)
type          EntityType enum (person, company, domain, email, …)
label         human-readable display name
properties    dict of additional data to show in the detail panel
source_module name of the module that produced this entity
source_url    optional link to the original source record
```

**Relationship** — a directed edge between two entities:
```
source_id     id of the originating entity
target_id     id of the target entity
type          ALL_CAPS_UNDERSCORE string describing the relationship
properties    dict of additional data
source_module name of the module that produced this relationship
```

---

## Entity IDs

Entity IDs must be **stable and deterministic** — running the same query twice should
produce the same IDs so duplicate entities are merged rather than duplicated.

Use a short hash of the canonical value:

```python
import hashlib

def entity_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.md5(value.lower().encode()).hexdigest()[:8]}"

# Examples
entity_id("domain", "example.com")   # → "domain_1a2b3c4d"
entity_id("email", "foo@bar.com")    # → "email_9f8e7d6c"
```

---

## T&S Risk Levels

Be honest. Understating risk puts operators at legal/civil exposure.

| Level | When to use |
|---|---|
| `none` | Official API with explicit programmatic access grant, or public domain data |
| `low` | HEAD/GET existence check only; no profile content extracted |
| `medium` | Programmatic access to public data with no explicit API; read hiQ v. LinkedIn |
| `high` | Likely T&S violation; module should display a prominent warning in the UI |

---

## Rate Limiting

Respect data source rate limits. Use `asyncio.sleep` between batched requests.
For free-tier APIs, document the limit in the module docstring.

---

## Error Handling

Never let exceptions propagate out of `execute()`. Catch them and return:

```python
except Exception as e:
    return ModuleResult(error=str(e))
```

---

## Testing Your Module

```bash
cd backend
pip install -r requirements.txt pytest pytest-asyncio
pytest tests/modules/test_your_module.py -v
```

Minimal test structure:

```python
import pytest
from app.modules.your_module import YourModule
from app.modules.base import Entity, EntityType

@pytest.mark.asyncio
async def test_execute_returns_result():
    module = YourModule()
    entity = Entity(id="test_1", type=EntityType.DOMAIN, label="example.com", source_module="test")
    result = await module.execute(entity)
    assert result.error is None
    assert len(result.entities) >= 0  # adjust based on expected output
```
