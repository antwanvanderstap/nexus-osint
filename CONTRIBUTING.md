# Contributing to Nexus OSINT

Thanks for contributing. The most impactful contributions are new modules — each one
expands what the community can investigate using clean, legal, public data.

---

## Adding a Module

### 1. Check the module request backlog first
Browse [open module requests](../../issues?q=label%3Amodule-request) before starting.
If your module isn't listed, open one so the community can weigh in on legal/T&S concerns
before you invest time building it.

### 2. Create your module file

Place it in `backend/app/modules/your_module_name.py` and subclass `BaseModule`:

```python
from app.modules.base import (
    BaseModule, Entity, EntityType, ModuleMetadata,
    ModuleResult, TosRisk, UseCase,
)

class YourModule(BaseModule):
    metadata = ModuleMetadata(
        name="your_module",
        display_name="Human-Readable Name",
        description="One sentence describing what this returns.",
        version="1.0.0",
        author="your-github-handle",
        data_source="Source Name",
        data_source_url="https://source-url.com",
        legal_uses=[UseCase.RESEARCH],
        prohibited_uses=[],          # Be honest — list real prohibited uses
        tos_risk=TosRisk.NONE,       # Be honest — see LEGAL.md for guidance
        requires_api_key=False,
        pii_returned=False,
        input_types=[EntityType.DOMAIN],
        output_types=[EntityType.COMPANY],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        # Your implementation
        ...
```

### 3. Register your module

Add it to `backend/app/modules/__init__.py`:

```python
from .your_module_name import YourModule

ALL_MODULES = [
    ...
    YourModule(),
]
```

### 4. Module checklist

Before opening a PR, confirm:

- [ ] `tos_risk` is accurate — do not understate it
- [ ] `prohibited_uses` is accurate — do not omit known restrictions
- [ ] `pii_returned` is set correctly
- [ ] The module uses `httpx.AsyncClient` with a reasonable timeout
- [ ] Errors are caught and returned via `ModuleResult(error=str(e))`
- [ ] No credentials are hardcoded
- [ ] The module respects rate limits of the data source
- [ ] A `User-Agent` header identifying nexus-osint is sent where applicable

### 5. Data sources we will not accept

The following will be rejected regardless of implementation quality:

- Modules that scrape content from authenticated social media sessions
- Modules that circumvent CAPTCHAs or bot detection
- Modules that aggregate data from other OSINT aggregators (Spokeo, BeenVerified, etc.)
- Modules that access non-public data without an explicit API grant
- Modules targeting a specific individual rather than a general data source

---

## Other Ways to Contribute

- **Bug reports** — use the bug report template
- **Legal review** — flag T&S or legal concerns on existing modules
- **Documentation** — operator guides, deployment docs, module docs
- **Frontend** — graph UX improvements, case management features
- **Testing** — add `pytest` tests under `backend/tests/`

---

## Code Style

- Python: follow PEP 8, use type hints throughout, async for all I/O
- TypeScript: strict mode, no `any` unless unavoidable
- No AI-generated boilerplate comments — code should be self-documenting

---

## License

By contributing, you agree your contributions are licensed under the MIT License.
