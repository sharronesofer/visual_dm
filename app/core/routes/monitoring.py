"""
Performance monitoring routes.
Provides endpoints for accessing system performance metrics.
"""

from flask import Blueprint, jsonify, current_app, request, send_file
from typing import Dict, Any
from app.core.utils.monitoring import track_performance
from app.core.utils.db_pool import ConnectionPoolManager
from flasgger import swag_from
from app.core.schemas.code_analysis_schemas import (
    PerformanceMetricsSchema,
    ErrorResponseSchema,
)
from app.core.utils.export_utils import export_to_csv, export_to_pdf
from app.core.api.error_handling.monitoring import ErrorMonitor
import io
from app.core.utils.email import send_monitoring_report_email

monitoring_bp = Blueprint("monitoring", __name__)


@monitoring_bp.route("/metrics", methods=["GET"])
@track_performance
@swag_from(
    {
        "tags": ["monitoring"],
        "summary": "Get system performance metrics",
        "description": "Get detailed performance metrics for routes, cache, database, and connection pool",
        "responses": {
            "200": {
                "description": "Performance metrics retrieved successfully",
                "schema": PerformanceMetricsSchema,
            },
            "503": {
                "description": "Performance monitoring not enabled",
                "schema": ErrorResponseSchema,
            },
        },
    }
)
def get_metrics():
    """Get system performance metrics."""
    monitor = current_app.extensions.get("performance_monitor")
    pool_manager = current_app.extensions.get("db_pool")

    if not monitor:
        return jsonify({"error": "Performance monitoring not enabled"}), 503

    metrics = {
        "routes": {},
        "cache": monitor.get_cache_stats(),
        "database": monitor.get_db_stats(),
    }

    # Add route-specific metrics
    for endpoint in current_app.view_functions:
        stats = monitor.get_route_stats(endpoint)
        if stats["count"] > 0:  # Only include routes with traffic
            metrics["routes"][endpoint] = stats

    # Add connection pool metrics if available
    if pool_manager:
        metrics["connection_pool"] = pool_manager.get_metrics()

    return jsonify(metrics)


@monitoring_bp.route("/metrics/reset", methods=["POST"])
@track_performance
def reset_metrics():
    """Reset all performance metrics."""
    monitor = current_app.extensions.get("performance_monitor")

    if not monitor:
        return jsonify({"error": "Performance monitoring not enabled"}), 503

    monitor.reset_metrics()
    return jsonify({"message": "Performance metrics reset successfully"})


@monitoring_bp.route("/metrics/export", methods=["GET"])
def export_metrics():
    """Export system performance metrics in CSV, PDF, or JSON format."""
    monitor = current_app.extensions.get("performance_monitor")
    if not monitor:
        return jsonify({"error": "Performance monitoring not enabled"}), 503
    metrics = {
        "routes": {},
        "cache": monitor.get_cache_stats(),
        "database": monitor.get_db_stats(),
    }
    for endpoint in current_app.view_functions:
        stats = monitor.get_route_stats(endpoint)
        if stats["count"] > 0:
            metrics["routes"][endpoint] = stats
    fmt = request.args.get("format", "json").lower()
    if fmt == "json":
        return jsonify(metrics)
    # Flatten metrics for CSV/PDF
    rows = []
    for route, stats in metrics["routes"].items():
        row = {"route": route}
        row.update(stats)
        rows.append(row)
    fieldnames = ["route", "count", "avg_time", "min_time", "max_time", "p95_time"]
    if fmt == "csv":
        csv_data = export_to_csv(rows, fieldnames)
        return send_file(
            io.BytesIO(csv_data.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="metrics.csv",
        )
    elif fmt == "pdf":
        try:
            pdf_data = export_to_pdf(rows, fieldnames, title="System Metrics Report")
        except ImportError:
            return jsonify({"error": "PDF export requires reportlab"}), 400
        return send_file(
            io.BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="metrics.pdf",
        )
    else:
        return jsonify({"error": "Unsupported format"}), 400


@monitoring_bp.route("/errors/export", methods=["GET"])
def export_errors():
    """Export error logs in CSV, PDF, or JSON format."""
    monitor = ErrorMonitor()
    errors = monitor.get_recent_errors(limit=1000)
    fmt = request.args.get("format", "json").lower()
    if fmt == "json":
        return jsonify(errors)
    # Flatten errors for CSV/PDF
    fieldnames = [
        "timestamp",
        "request_id",
        "error_type",
        "error_message",
        "user_id",
        "request_path",
    ]
    rows = []
    for e in errors:
        row = {
            "timestamp": e.get("timestamp"),
            "request_id": e.get("request_id"),
            "error_type": e.get("error_type"),
            "error_message": e.get("error_message"),
            "user_id": e.get("user_id", ""),
            "request_path": e.get("request", {}).get("path", ""),
        }
        rows.append(row)
    if fmt == "csv":
        csv_data = export_to_csv(rows, fieldnames)
        return send_file(
            io.BytesIO(csv_data.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="errors.csv",
        )
    elif fmt == "pdf":
        try:
            pdf_data = export_to_pdf(rows, fieldnames, title="Error Log Report")
        except ImportError:
            return jsonify({"error": "PDF export requires reportlab"}), 400
        return send_file(
            io.BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="errors.pdf",
        )
    else:
        return jsonify({"error": "Unsupported format"}), 400


def send_scheduled_monitoring_report(fmt: str = "csv"):
    """
    Generate and send a scheduled monitoring report email to the admin.
    Args:
        fmt: 'csv' or 'pdf'
    """
    app = current_app._get_current_object()
    admin_email = app.config.get("ADMIN_EMAIL") or app.config.get("MAIL_DEFAULT_SENDER")
    # --- Metrics ---
    monitor = app.extensions.get("performance_monitor")
    if not monitor:
        return
    metrics = {
        "routes": {},
        "cache": monitor.get_cache_stats(),
        "database": monitor.get_db_stats(),
    }
    for endpoint in app.view_functions:
        stats = monitor.get_route_stats(endpoint)
        if stats["count"] > 0:
            metrics["routes"][endpoint] = stats
    metrics_rows = []
    for route, stats in metrics["routes"].items():
        row = {"route": route}
        row.update(stats)
        metrics_rows.append(row)
    metrics_fieldnames = [
        "route",
        "count",
        "avg_time",
        "min_time",
        "max_time",
        "p95_time",
    ]
    # --- Errors ---
    error_monitor = ErrorMonitor()
    errors = error_monitor.get_recent_errors(limit=1000)
    errors_fieldnames = [
        "timestamp",
        "request_id",
        "error_type",
        "error_message",
        "user_id",
        "request_path",
    ]
    errors_rows = []
    for e in errors:
        row = {
            "timestamp": e.get("timestamp"),
            "request_id": e.get("request_id"),
            "error_type": e.get("error_type"),
            "error_message": e.get("error_message"),
            "user_id": e.get("user_id", ""),
            "request_path": e.get("request", {}).get("path", ""),
        }
        errors_rows.append(row)
    # --- Send Email ---
    send_monitoring_report_email(
        recipient=admin_email,
        metrics_data=metrics_rows,
        metrics_fieldnames=metrics_fieldnames,
        errors_data=errors_rows,
        errors_fieldnames=errors_fieldnames,
        fmt=fmt,
        subject="Scheduled System Monitoring Report",
        body="<p>Attached are the latest system metrics and error logs.</p>",
    )
