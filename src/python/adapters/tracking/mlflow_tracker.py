from __future__ import annotations

import logging

import mlflow

from ...domain.models import ComplianceReport

logger = logging.getLogger(__name__)


class MLflowTracker:
    """Experiment tracking adapter using MLflow."""

    def __init__(
        self,
        tracking_uri: str = "http://localhost:5000",
        experiment_name: str = "ai-tauron-compliance",
    ) -> None:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self._active_run = None
        logger.info("MLflow tracker: uri=%s, experiment=%s", tracking_uri, experiment_name)

    def start_run(self, run_name: str, tags: dict[str, str] | None = None) -> str:
        # End any stale run left from a previous crash/timeout
        if mlflow.active_run():
            mlflow.end_run()
        self._active_run = mlflow.start_run(run_name=run_name, tags=tags)
        return self._active_run.info.run_id

    def log_params(self, params: dict[str, str]) -> None:
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        mlflow.log_metrics(metrics)

    def log_prompt(self, prompt_name: str, prompt_template: str, version: str) -> None:
        mlflow.log_text(prompt_template, f"prompts/{prompt_name}_v{version}.txt")
        mlflow.set_tag(f"prompt.{prompt_name}.version", version)

    def log_artifact(self, local_path: str) -> None:
        mlflow.log_artifact(local_path)

    def log_report(self, report: ComplianceReport) -> None:
        report_json = report.model_dump_json(indent=2)
        mlflow.log_text(report_json, f"reports/{report.document_name}_{report.id}.json")
        mlflow.log_metrics({
            "total_findings": float(report.total_findings),
            "critical_count": float(report.critical_count),
            "high_count": float(report.high_count),
            "medium_count": float(report.medium_count),
            "low_count": float(report.low_count),
        })

    def end_run(self) -> None:
        if self._active_run:
            mlflow.end_run()
            self._active_run = None
