"""Append-only local activity/evidence ledger.

The ledger records neutral facts. It intentionally contains no airdrop scoring
or spend-maximization logic while genesis conversion rules remain unresolved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True, slots=True)
class ActivityRecord:
    timestamp: str
    kind: str
    channel_id: str | None
    data: dict[str, Any]


class EvidenceLedger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(
        self,
        kind: str,
        *,
        channel_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> ActivityRecord:
        if not kind:
            raise ValueError("kind is required")
        record = ActivityRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            channel_id=channel_id,
            data=data or {},
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(self._canonical(record) + "\n")
        return record

    def records(self) -> Iterator[ActivityRecord]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                yield ActivityRecord(**payload)

    def sha256(self) -> str:
        digest = hashlib.sha256()
        if self.path.exists():
            digest.update(self.path.read_bytes())
        return digest.hexdigest()

    @staticmethod
    def _canonical(record: ActivityRecord) -> str:
        return json.dumps(
            asdict(record),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
