"""
opena17_Analytics: Analytics & Reporting Agent
KPI dashboards, trend analysis, report generation, metrics aggregation
GitHub Pattern: Skyscope-AI (analytics_business_intelligence.py) + Ad-rah (analytics_reporting.py)
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
import sys
import secrets
import statistics

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena17_Analytics",
    version="1.0.0",
    description="Analytics Agent - Reporting & KPI Dashboards"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12365
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_reports: Dict[str, dict] = {}
_metrics_cache: Dict[str, dict] = {}
_dashboards: Dict[str, dict] = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class ReportRequest(BaseModel):
    title: str
    start_date: str  # ISO 8601
    end_date: str    # ISO 8601
    metrics: List[str]  # revenue, users, conversions, deals, etc.
    format: str = "json"  # json, csv, pdf


class MetricsAggregationRequest(BaseModel):
    metrics: List[str]  # Which metrics to aggregate from other agents


class DashboardRequest(BaseModel):
    name: str
    metrics: List[str]
    refresh_interval: int = 300  # seconds


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: Optional[str]):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena17_analytics",
            "dst": "opena2",
            "kind": "ANALYTICS_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"}
        }
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_report_id() -> str:
    """Generate unique report ID"""
    return f"RPT_{secrets.token_hex(8).upper()}"


def _generate_dashboard_id() -> str:
    """Generate unique dashboard ID"""
    return f"DASH_{secrets.token_hex(6).upper()}"


def _calculate_trend(current: float, previous: float) -> Dict[str, Any]:
    """Calculate trend analysis"""
    if previous == 0:
        change_pct = 100.0 if current > 0 else 0.0
    else:
        change_pct = ((current - previous) / abs(previous)) * 100
    
    trend = "up" if change_pct > 0 else "down" if change_pct < 0 else "stable"
    
    return {
        "trend": trend,
        "change_percentage": round(change_pct, 2),
        "current": current,
        "previous": previous
    }


def _simulate_metrics() -> Dict[str, Dict[str, float]]:
    """Simulate metrics from various agents"""
    return {
        "revenue": {
            "current": 125000.00,
            "previous": 100000.00,
            "unit": "USD"
        },
        "active_users": {
            "current": 5234,
            "previous": 4800,
            "unit": "count"
        },
        "conversions": {
            "current": 892,
            "previous": 756,
            "unit": "count"
        },
        "deals_pipeline": {
            "current": 45000.00,
            "previous": 38000.00,
            "unit": "USD"
        },
        "customer_satisfaction": {
            "current": 4.7,
            "previous": 4.5,
            "unit": "score"
        },
        "email_sent": {
            "current": 23450,
            "previous": 21000,
            "unit": "count"
        },
        "social_posts": {
            "current": 567,
            "previous": 480,
            "unit": "count"
        }
    }


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena17_Analytics",
        "port": PORT,
        "reports": len(_reports),
        "dashboards": len(_dashboards),
        "cached_metrics": len(_metrics_cache),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/report/generate")
async def generate_report(req: ReportRequest, authorization: str = Header(None)):
    """Generate custom report"""
    _validate_token(authorization)
    
    try:
        report_id = _generate_report_id()
        
        # Simulate metric aggregation
        metrics_data = {}
        all_metrics = _simulate_metrics()
        
        for metric_name in req.metrics:
            if metric_name in all_metrics:
                metric = all_metrics[metric_name]
                metrics_data[metric_name] = {
                    **metric,
                    "trend": _calculate_trend(metric["current"], metric["previous"])
                }
        
        report_entry = {
            "id": report_id,
            "title": req.title,
            "date_range": {
                "start": req.start_date,
                "end": req.end_date
            },
            "metrics": metrics_data,
            "format": req.format,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        _reports[report_id] = report_entry
        
        logger.info(f"📄 Report generated: {report_id} ({req.title})")
        
        await _archive({
            "op": "REPORT_GENERATED",
            "report_id": report_id,
            "title": req.title,
            "metrics_count": len(req.metrics),
            "format": req.format
        })
        
        return {
            "strict": True,
            "report_id": report_id,
            "title": req.title,
            "metrics_count": len(req.metrics),
            "generated": True,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/{report_id}")
async def get_report(report_id: str, authorization: str = Header(None)):
    """Get report details"""
    _validate_token(authorization)
    
    try:
        if report_id not in _reports:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
        
        report = _reports[report_id]
        
        logger.info(f"📋 Report retrieved: {report_id}")
        
        return {
            "strict": True,
            "report": report,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Report retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/metrics/aggregate")
async def aggregate_metrics(req: MetricsAggregationRequest, authorization: str = Header(None)):
    """Aggregate metrics from all agents"""
    _validate_token(authorization)
    
    try:
        # Simulate metric collection from all agents
        all_metrics = _simulate_metrics()
        
        aggregated = {}
        for metric_name in req.metrics:
            if metric_name in all_metrics:
                metric = all_metrics[metric_name]
                aggregated[metric_name] = {
                    "value": metric["current"],
                    "unit": metric["unit"],
                    "trend": _calculate_trend(metric["current"], metric["previous"])
                }
        
        _metrics_cache.update(aggregated)
        
        logger.info(f"📊 Metrics aggregated: {len(aggregated)} metrics")
        
        await _archive({
            "op": "METRICS_AGGREGATED",
            "metrics_count": len(aggregated),
            "metric_names": list(aggregated.keys())
        })
        
        return {
            "strict": True,
            "aggregated_metrics": aggregated,
            "count": len(aggregated),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Metrics aggregation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/dashboard")
async def get_dashboard_overview(authorization: str = Header(None)):
    """Get dashboard overview with KPIs"""
    _validate_token(authorization)
    
    try:
        metrics = _simulate_metrics()
        
        # Calculate KPIs
        kpis = {}
        for metric_name, metric_data in metrics.items():
            kpis[metric_name] = {
                "current": metric_data["current"],
                "previous": metric_data["previous"],
                "unit": metric_data["unit"],
                **_calculate_trend(metric_data["current"], metric_data["previous"])
            }
        
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "kpis": kpis,
            "summary": {
                "total_metrics": len(kpis),
                "metrics_up": sum(1 for k in kpis.values() if k["trend"] == "up"),
                "metrics_down": sum(1 for k in kpis.values() if k["trend"] == "down")
            }
        }
        
        logger.info(f"📊 Dashboard overview retrieved")
        
        return {
            "strict": True,
            "dashboard": dashboard,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Dashboard retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trends/{metric_name}")
async def get_trend_analysis(metric_name: str, authorization: str = Header(None)):
    """Get trend analysis for a specific metric"""
    _validate_token(authorization)
    
    try:
        metrics = _simulate_metrics()
        
        if metric_name not in metrics:
            raise HTTPException(status_code=404, detail=f"Metric {metric_name} not found")
        
        metric = metrics[metric_name]
        
        # Simulate historical data
        historical_values = [
            metric["previous"] * (0.8 + i * 0.05) for i in range(10)
        ]
        
        trend_analysis = {
            "metric_name": metric_name,
            "current_value": metric["current"],
            "historical_values": historical_values[-10:],  # Last 10 data points
            "average": statistics.mean(historical_values),
            "min": min(historical_values),
            "max": max(historical_values),
            "std_dev": statistics.stdev(historical_values) if len(historical_values) > 1 else 0,
            "trend": _calculate_trend(metric["current"], metric["previous"])
        }
        
        logger.info(f"📈 Trend analysis: {metric_name}")
        
        await _archive({
            "op": "TREND_ANALYZED",
            "metric": metric_name,
            "current": metric["current"],
            "trend_direction": trend_analysis["trend"]["trend"]
        })
        
        return {
            "strict": True,
            "trend_analysis": trend_analysis,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/pdf")
async def export_report_pdf(report_id: str, authorization: str = Header(None)):
    """Export report to PDF (simulated)"""
    _validate_token(authorization)
    
    try:
        if report_id not in _reports:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
        
        report = _reports[report_id]
        
        # Simulate PDF export
        export_data = {
            "filename": f"{report_id}_report.pdf",
            "size_bytes": len(json.dumps(report)) * 2,  # Rough estimate
            "exported_at": datetime.utcnow().isoformat(),
            "format": "PDF",
            "status": "completed"
        }
        
        logger.info(f"💾 Report exported to PDF: {report_id}")
        
        await _archive({
            "op": "EXPORT_PDF",
            "report_id": report_id,
            "filename": export_data["filename"],
            "size_bytes": export_data["size_bytes"]
        })
        
        return {
            "strict": True,
            "export": export_data,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena17_Analytics",
        "version": "1.0.0",
        "port": PORT,
        "reports_generated": len(_reports),
        "dashboards": len(_dashboards),
        "cached_metrics": len(_metrics_cache),
        "endpoints": 7,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena17_Analytics on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
