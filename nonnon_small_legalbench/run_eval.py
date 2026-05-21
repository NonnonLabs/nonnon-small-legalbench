from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from tqdm import tqdm

import config
from nonnon_small_legalbench.client import NonnonClient, extract_text
from nonnon_small_legalbench.load_tasks import load_rows, select_tasks
from nonnon_small_legalbench.prompt_builder import load_base_prompt, render_prompt
from nonnon_small_legalbench.score import score_prediction


def _answer_field(row: dict[str, object]) -> object:
    for key in ("answer", "label", "reference"):
        if key in row:
            return row[key]
    raise KeyError("row has no answer, label, or reference field")


def _run_one(
    *,
    client: NonnonClient,
    model: str,
    task: str,
    prompt: str,
    reference: object,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    started = time.time()
    error = None
    prediction = ""
    score = 0.0
    try:
        response = client.chat_completion(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        prediction = extract_text(response)
        score = score_prediction(prediction, reference)
    except Exception as exc:  # pragma: no cover - network dependent
        error = f"{type(exc).__name__}: {exc}"
    return {
        "task": task,
        "reference": str(reference),
        "prediction": prediction,
        "score": score,
        "latency_seconds": round(time.time() - started, 3),
        "error": error,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    load_dotenv(dotenv_path=Path(".env"), override=False)
    api_key = os.getenv("NONNON_API_KEY")
    if not api_key:
        raise SystemExit("Set NONNON_API_KEY in the environment or .env")

    tasks = ["abercrombie"] if args.smoke else select_tasks(args.tasks)
    max_examples = 1 if args.smoke else args.max_examples
    client = NonnonClient(
        api_key=api_key,
        base_url=args.base_url,
        timeout_seconds=args.timeout_seconds,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.results_dir) / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    task_summaries: dict[str, dict[str, Any]] = {}
    all_scores: list[float] = []
    all_errors = 0

    for task in tasks:
        rows = load_rows(task, split=args.split, max_examples=max_examples)
        template = load_base_prompt(task)
        jobs: list[tuple[str, object]] = []
        for row in rows:
            jobs.append((render_prompt(template, row), _answer_field(row)))

        results: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [
                pool.submit(
                    _run_one,
                    client=client,
                    model=args.model,
                    task=task,
                    prompt=prompt,
                    reference=reference,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                for prompt, reference in jobs
            ]
            for future in tqdm(as_completed(futures), total=len(futures), desc=task):
                result = future.result()
                results.append(result)
                all_scores.append(float(result["score"]))
                if result["error"]:
                    all_errors += 1

        task_score = sum(float(item["score"]) for item in results) / max(len(results), 1)
        task_summaries[task] = {
            "score": task_score,
            "total": len(results),
            "errors": sum(1 for item in results if item["error"]),
        }
        (out_dir / f"{task}.json").write_text(
            json.dumps({"task": task, "results": results}, indent=2),
            encoding="utf-8",
        )

    macro = sum(item["score"] for item in task_summaries.values()) / max(len(task_summaries), 1)
    micro = sum(all_scores) / max(len(all_scores), 1)
    summary = {
        "evaluated_at": timestamp,
        "base_url": args.base_url,
        "model": args.model,
        "split": args.split,
        "task_count": len(task_summaries),
        "total": len(all_scores),
        "macro": macro,
        "micro": micro,
        "errors": all_errors,
        "task_scores": task_summaries,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate NONNON-small on public LegalBench tasks.")
    parser.add_argument("--smoke", action="store_true", help="run one abercrombie example")
    parser.add_argument("--tasks", default=config.DEFAULT_TASKS, help="comma-separated task ids or all")
    parser.add_argument("--split", default=config.DEFAULT_SPLIT)
    parser.add_argument("--max-examples", type=int, default=config.DEFAULT_MAX_EXAMPLES)
    parser.add_argument("--concurrency", type=int, default=config.DEFAULT_CONCURRENCY)
    parser.add_argument("--timeout-seconds", type=float, default=config.DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--base-url", default=os.getenv("NONNON_BASE_URL", config.BASE_URL))
    parser.add_argument("--model", default=config.MODEL)
    parser.add_argument("--temperature", type=float, default=config.DEFAULT_TEMPERATURE)
    parser.add_argument("--max-tokens", type=int, default=config.DEFAULT_MAX_TOKENS)
    parser.add_argument("--results-dir", default=config.RESULTS_DIR)
    return parser


def main() -> int:
    run(build_parser().parse_args())
    return 0
