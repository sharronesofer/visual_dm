from typing import Any


class Transaction:
    commit(): Awaitable[None>
    rollback(): Awaitable[None>
    isActive(): bool