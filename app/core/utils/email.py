"""
Email utility functions for sending system emails.
"""

from typing import Optional
from flask import current_app, render_template_string
from flask_mail import Message, Mail
from threading import Thread
from app.core.utils.export_utils import export_to_csv, export_to_pdf

# Initialize Flask-Mail
mail = Mail()


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)


def send_email(subject: str, recipient: str, template: str, **kwargs) -> None:
    """
    Send an email using a template.

    Args:
        subject: Email subject
        recipient: Recipient email address
        template: HTML template string
        **kwargs: Template variables
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        recipients=[recipient],
        html=render_template_string(template, **kwargs),
        sender=app.config["MAIL_DEFAULT_SENDER"],
    )

    if app.config["TESTING"]:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(app, msg)).start()


def send_verification_email(email: str, token: str) -> None:
    """
    Send an email verification link.

    Args:
        email: Recipient email address
        token: Verification token
    """
    verification_link = f"{current_app.config['FRONTEND_URL']}/verify-email/{token}"
    template = """
    <p>Welcome! Please verify your email address by clicking the link below:</p>
    <p><a href="{{ verification_link }}">Verify Email</a></p>
    <p>If you didn't create an account, you can safely ignore this email.</p>
    <p>This link will expire in 24 hours.</p>
    """

    send_email(
        subject="Verify Your Email Address",
        recipient=email,
        template=template,
        verification_link=verification_link,
    )


def send_password_reset_email(email: str, token: str) -> None:
    """
    Send a password reset link.

    Args:
        email: Recipient email address
        token: Password reset token
    """
    reset_link = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"
    template = """
    <p>You have requested to reset your password. Click the link below to proceed:</p>
    <p><a href="{{ reset_link }}">Reset Password</a></p>
    <p>If you didn't request a password reset, you can safely ignore this email.</p>
    <p>This link will expire in 1 hour.</p>
    """

    send_email(
        subject="Reset Your Password",
        recipient=email,
        template=template,
        reset_link=reset_link,
    )


def send_monitoring_report_email(
    recipient: str,
    metrics_data: list,
    metrics_fieldnames: list,
    errors_data: list,
    errors_fieldnames: list,
    fmt: str = "csv",
    subject: str = "System Monitoring Report",
    body: str = None,
) -> None:
    """
    Send a monitoring report email with attached metrics and error logs.
    Args:
        recipient: Email address to send to
        metrics_data: List of dicts for metrics
        metrics_fieldnames: List of fieldnames for metrics
        errors_data: List of dicts for errors
        errors_fieldnames: List of fieldnames for errors
        fmt: 'csv' or 'pdf'
        subject: Email subject
        body: Optional HTML body
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        recipients=[recipient],
        html=body or "<p>See attached system monitoring report.</p>",
        sender=app.config["MAIL_DEFAULT_SENDER"],
    )
    # Attach metrics
    if fmt == "csv":
        metrics_bytes = export_to_csv(metrics_data, metrics_fieldnames).encode("utf-8")
        errors_bytes = export_to_csv(errors_data, errors_fieldnames).encode("utf-8")
        msg.attach("metrics.csv", "text/csv", metrics_bytes)
        msg.attach("errors.csv", "text/csv", errors_bytes)
    elif fmt == "pdf":
        metrics_bytes = export_to_pdf(
            metrics_data, metrics_fieldnames, title="System Metrics Report"
        )
        errors_bytes = export_to_pdf(
            errors_data, errors_fieldnames, title="Error Log Report"
        )
        msg.attach("metrics.pdf", "application/pdf", metrics_bytes)
        msg.attach("errors.pdf", "application/pdf", errors_bytes)
    else:
        raise ValueError("Unsupported format for report email")
    if app.config["TESTING"]:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(app, msg)).start()
