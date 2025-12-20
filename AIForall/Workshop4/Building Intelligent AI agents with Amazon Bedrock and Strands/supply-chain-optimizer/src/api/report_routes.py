"""Report retrieval API endpoints."""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
from typing import Dict, Any
import io
import json

from src.config import logger, config
from src.api.auth import APIAuth
from src.database.connection import get_rds_session
from src.database.schema import ReportTable
from src.aws import get_s3_client


report_bp = Blueprint("report", __name__, url_prefix="/api/reports")


@report_bp.route("", methods=["GET"])
@APIAuth.require_auth
def list_reports() -> tuple:
    """List reports with optional filtering.
    
    Query Parameters:
        - report_type: Filter by type (daily, weekly, monthly, custom)
        - start_date: Filter by start date (YYYY-MM-DD)
        - end_date: Filter by end date (YYYY-MM-DD)
        - limit: Number of results (default: 50)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON with report records
    """
    try:
        report_type = request.args.get("report_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        if limit < 1 or limit > 500:
            return jsonify({"error": "Limit must be between 1 and 500"}), 400

        session = get_rds_session()

        try:
            query = session.query(ReportTable)

            if report_type:
                query = query.filter(ReportTable.report_type == report_type)

            if start_date:
                try:
                    start = datetime.fromisoformat(start_date).date()
                    query = query.filter(ReportTable.period_start >= start)
                except ValueError:
                    return jsonify({"error": "Invalid start_date format (use YYYY-MM-DD)"}), 400

            if end_date:
                try:
                    end = datetime.fromisoformat(end_date).date()
                    query = query.filter(ReportTable.period_end <= end)
                except ValueError:
                    return jsonify({"error": "Invalid end_date format (use YYYY-MM-DD)"}), 400

            total_count = query.count()
            results = query.order_by(ReportTable.generated_at.desc()).limit(limit).offset(offset).all()

            logger.info(f"Listed reports: type={report_type}, count={len(results)}")

            return jsonify({
                "data": [r.dict() for r in results],
                "total": total_count,
                "limit": limit,
                "offset": offset,
            }), 200

        finally:
            session.close()

    except ValueError as e:
        logger.error(f"Invalid query parameters: {str(e)}")
        return jsonify({"error": "Invalid query parameters"}), 400
    except Exception as e:
        logger.error(f"Failed to list reports: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@report_bp.route("/<report_id>", methods=["GET"])
@APIAuth.require_auth
def get_report(report_id: str) -> tuple:
    """Get report by ID.
    
    Args:
        report_id: Report ID
    
    Returns:
        JSON with report details
    """
    try:
        session = get_rds_session()

        try:
            report = session.query(ReportTable).filter(
                ReportTable.report_id == report_id
            ).first()

            if not report:
                logger.warning(f"Report not found: {report_id}")
                return jsonify({"error": "Report not found"}), 404

            logger.info(f"Retrieved report: {report_id}")
            return jsonify(report.dict()), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get report: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@report_bp.route("/<report_id>/download", methods=["GET"])
@APIAuth.require_auth
def download_report(report_id: str) -> tuple:
    """Download report file from S3.
    
    Args:
        report_id: Report ID
    
    Returns:
        File download or error
    """
    try:
        session = get_rds_session()

        try:
            report = session.query(ReportTable).filter(
                ReportTable.report_id == report_id
            ).first()

            if not report:
                logger.warning(f"Report not found: {report_id}")
                return jsonify({"error": "Report not found"}), 404

            # Download from S3
            s3_client = get_s3_client()
            s3_key = f"reports/{report_id}.json"

            try:
                response = s3_client.get_object(
                    Bucket=config.s3.bucket_name,
                    Key=s3_key
                )

                file_content = response["Body"].read()
                logger.info(f"Downloaded report from S3: {report_id}")

                return send_file(
                    io.BytesIO(file_content),
                    mimetype="application/json",
                    as_attachment=True,
                    download_name=f"{report_id}.json"
                ), 200

            except s3_client.exceptions.NoSuchKey:
                logger.warning(f"Report file not found in S3: {s3_key}")
                return jsonify({"error": "Report file not found"}), 404

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to download report: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@report_bp.route("/latest/<report_type>", methods=["GET"])
@APIAuth.require_auth
def get_latest_report(report_type: str) -> tuple:
    """Get latest report of a specific type.
    
    Args:
        report_type: Report type (daily, weekly, monthly, custom)
    
    Returns:
        JSON with latest report
    """
    try:
        valid_types = ["daily", "weekly", "monthly", "custom"]
        if report_type not in valid_types:
            return jsonify({"error": f"Invalid report type. Must be one of: {valid_types}"}), 400

        session = get_rds_session()

        try:
            report = session.query(ReportTable).filter(
                ReportTable.report_type == report_type
            ).order_by(ReportTable.generated_at.desc()).first()

            if not report:
                logger.warning(f"No reports found for type: {report_type}")
                return jsonify({"error": "No reports found"}), 404

            logger.info(f"Retrieved latest report: type={report_type}, id={report.report_id}")
            return jsonify(report.dict()), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get latest report: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@report_bp.route("/period", methods=["GET"])
@APIAuth.require_auth
def get_reports_by_period() -> tuple:
    """Get reports for a specific period.
    
    Query Parameters:
        - start_date: Period start (YYYY-MM-DD, required)
        - end_date: Period end (YYYY-MM-DD, required)
    
    Returns:
        JSON with reports in period
    """
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            return jsonify({"error": "start_date and end_date are required"}), 400

        try:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
        except ValueError:
            return jsonify({"error": "Invalid date format (use YYYY-MM-DD)"}), 400

        if start > end:
            return jsonify({"error": "start_date must be before end_date"}), 400

        session = get_rds_session()

        try:
            reports = session.query(ReportTable).filter(
                ReportTable.period_start >= start,
                ReportTable.period_end <= end
            ).order_by(ReportTable.generated_at.desc()).all()

            logger.info(f"Retrieved {len(reports)} reports for period {start} to {end}")

            return jsonify({
                "data": [r.dict() for r in reports],
                "count": len(reports),
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                }
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to get reports by period: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
