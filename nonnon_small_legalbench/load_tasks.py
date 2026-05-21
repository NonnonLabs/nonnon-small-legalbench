from __future__ import annotations

from collections.abc import Iterable

from datasets import get_dataset_config_names, load_dataset


DATASET_ID = "nguha/legalbench"


def available_tasks() -> list[str]:
    return sorted(get_dataset_config_names(DATASET_ID))


def select_tasks(tasks: str | Iterable[str]) -> list[str]:
    if isinstance(tasks, str):
        if tasks.lower() == "all":
            return available_tasks()
        return [part.strip() for part in tasks.split(",") if part.strip()]
    return list(tasks)


def load_rows(task: str, *, split: str, max_examples: int | None) -> list[dict[str, object]]:
    dataset = load_dataset(DATASET_ID, task, split=split)
    rows = list(dataset)
    if max_examples is not None:
        rows = rows[:max_examples]
    return [dict(row) for row in rows]
