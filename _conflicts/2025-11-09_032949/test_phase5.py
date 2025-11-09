"""
Phase 5 Integration Tests: Agents 16-19
CRM, Analytics, Dashboard, Workflow
"""

import json
import time
import urllib.request

import pytest

# Configuration
TOKEN = "MEIN_SUPER_TOKEN_123"
AGENTS = {
    "crm": ("opena16_CRM", 12364),
    "analytics": ("opena17_Analytics", 12365),
    "dashboard": ("opena18_Dashboard", 12366),
    "workflow": ("opena19_Workflow", 12367),
}


def _post(port: int, path: str, payload: dict) -> dict:
    """POST request helper"""
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"❌ POST {url}: {e}")
        raise


def _get(port: int, path: str) -> dict:
    """GET request helper"""
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {TOKEN}"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"❌ GET {url}: {e}")
        raise


def _health(port: int) -> dict:
    """Health check without auth"""
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"❌ Health check {url}: {e}")
        return None


# ==========================================================================
# FIXTURES
# ==========================================================================


@pytest.fixture(scope="module")
def crm_customer() -> dict:
    """Create a CRM customer once per test module."""
    port = AGENTS["crm"][1]
    unique_suffix = int(time.time())
    payload = {
        "name": f"Test Corp {unique_suffix}",
        "email": f"contact{unique_suffix}@test.com",
        "phone": "+1234567890",
        "company": "Test Corporation",
        "lifecycle_stage": "prospect",
    }
    result = _post(port, "/customer/create", payload)
    assert result.get("created") is True
    return {"id": result["customer_id"], "payload": payload}


@pytest.fixture(scope="module")
def crm_deal(crm_customer: dict) -> str:
    """Create a CRM deal linked to the fixture customer."""
    port = AGENTS["crm"][1]
    payload = {
        "customer_id": crm_customer["id"],
        "title": "Test Deal",
        "amount": 50000.0,
        "stage": "proposal",
        "close_date": "2025-12-31",
    }
    result = _post(port, "/deal/create", payload)
    assert result.get("created") is True
    return result["deal_id"]


@pytest.fixture(scope="module")
def analytics_report() -> str:
    """Generate a report once for analytics tests."""
    port = AGENTS["analytics"][1]
    unique_suffix = int(time.time())
    payload = {
        "title": f"Monthly Report {unique_suffix}",
        "start_date": "2025-11-01",
        "end_date": "2025-11-30",
        "metrics": ["revenue", "active_users", "conversions"],
        "format": "json",
    }
    result = _post(port, "/report/generate", payload)
    assert result.get("generated") is True
    return result["report_id"]


@pytest.fixture(scope="module")
def dashboard_widget() -> str:
    """Provision a dashboard widget for dependent tests."""
    port = AGENTS["dashboard"][1]
    unique_suffix = int(time.time())
    payload = {
        "title": f"Revenue Widget {unique_suffix}",
        "type": "metric",
        "data_source": "analytics",
        "refresh_interval": 60,
    }
    result = _post(port, "/widget/create", payload)
    assert result.get("created") is True
    return result["widget_id"]


@pytest.fixture(scope="module")
def dashboard_layout(dashboard_widget: str) -> str:
    """Save a dashboard layout referencing the created widget."""
    port = AGENTS["dashboard"][1]
    payload = {
        "name": "Main Dashboard",
        "widgets": [dashboard_widget],
        "grid_config": {"columns": 2, "rows": 2},
    }
    result = _post(port, "/layout/save", payload)
    assert result.get("saved") is True
    return result["layout_id"]


@pytest.fixture(scope="module")
def workflow_id() -> str:
    """Create a workflow once for workflow-related tests."""
    port = AGENTS["workflow"][1]
    unique_suffix = int(time.time())
    payload = {
        "name": f"Sales Pipeline {unique_suffix}",
        "description": "Automate sales process",
        "steps": [
            {
                "step_id": "step1",
                "action": "call_agent",
                "target": "crm",
                "payload": {"type": "create_customer"},
            },
            {
                "step_id": "step2",
                "action": "call_agent",
                "target": "analytics",
                "payload": {"type": "generate_report"},
            },
        ],
        "enabled": True,
    }
    result = _post(port, "/workflow/create", payload)
    assert result.get("created") is True
    return result["workflow_id"]


@pytest.fixture(scope="module")
def workflow_execution_result(workflow_id: str) -> dict:
    """Execute the workflow once and share the execution payload."""
    port = AGENTS["workflow"][1]
    payload = {"context": {"customer_name": "Test Corp", "amount": 50000}}
    result = _post(port, f"/workflow/{workflow_id}/execute", payload)
    assert result.get("status") in {"completed", "failed"}
    assert "execution_id" in result
    return result


@pytest.fixture(scope="module")
def workflow_trigger_id(workflow_id: str) -> str:
    """Register a trigger for the workflow once."""
    port = AGENTS["workflow"][1]
    payload = {
        "event_type": "schedule",
        "condition": "0 8 * * MON",
        "workflow_id": workflow_id,
    }
    result = _post(port, "/trigger/set", payload)
    assert result.get("created") is True
    return result["trigger_id"]


# ============================================================================
# TEST: Agent 16 (CRM)
# ============================================================================

def test_crm_create_customer(crm_customer: dict):
    assert crm_customer["id"].startswith("CUST_")
    print(f"✅ CRM: Customer created: {crm_customer['id']}")


def test_crm_get_customer(crm_customer: dict):
    port = AGENTS["crm"][1]
    result = _get(port, f"/customer/{crm_customer['id']}")
    assert result.get("customer") is not None
    print(f"✅ CRM: Customer retrieved: {crm_customer['id']}")


def test_crm_log_interaction(crm_customer: dict):
    port = AGENTS["crm"][1]
    payload = {
        "type": "email",
        "notes": "Sent proposal",
        "outcome": "positive",
    }
    result = _post(port, f"/customer/{crm_customer['id']}/contact", payload)
    assert result.get("interaction_logged") is True
    print(f"✅ CRM: Interaction logged for {crm_customer['id']}")


def test_crm_create_deal(crm_deal: str):
    assert crm_deal.startswith("DEAL_")
    print(f"✅ CRM: Deal created: {crm_deal}")


def test_crm_update_deal(crm_deal: str):
    port = AGENTS["crm"][1]
    payload = {"stage": "negotiation", "notes": "Price negotiated"}
    result = _post(port, f"/deal/{crm_deal}/update", payload)
    assert result.get("updated") is True
    print(f"✅ CRM: Deal updated: {crm_deal}")


def test_crm_status(crm_customer: dict, crm_deal: str):
    port = AGENTS["crm"][1]
    result = _get(port, "/status")
    assert result.get("service") == "opena16_CRM"
    assert result.get("total_customers", 0) >= 1
    assert result.get("total_deals", 0) >= 1
    print(f"✅ CRM: Status - Leads: {result.get('leads')}, Customers: {result.get('customers')}")


# ============================================================================
# TEST: Agent 17 (Analytics)
# ============================================================================

def test_analytics_generate_report(analytics_report: str):
    assert analytics_report.startswith("RPT_")
    print(f"✅ Analytics: Report generated: {analytics_report}")


def test_analytics_get_report(analytics_report: str):
    port = AGENTS["analytics"][1]
    result = _get(port, f"/report/{analytics_report}")
    assert result.get("report") is not None
    print(f"✅ Analytics: Report retrieved: {analytics_report}")


def test_analytics_aggregate_metrics():
    """Test: Aggregate metrics"""
    port = AGENTS["analytics"][1]
    
    payload = {
        "metrics": ["revenue", "conversions", "customer_satisfaction"]
    }
    
    result = _post(port, "/metrics/aggregate", payload)
    assert result.get("count") > 0
    print(f"✅ Analytics: Metrics aggregated: {result['count']} metrics")


def test_analytics_dashboard():
    """Test: Get dashboard overview"""
    port = AGENTS["analytics"][1]
    
    result = _get(port, "/analytics/dashboard")
    assert result.get("dashboard") is not None
    dashboard = result["dashboard"]
    print(f"✅ Analytics: Dashboard - {dashboard['summary']['total_metrics']} metrics")


def test_analytics_trend(metric_name: str = "revenue"):
    """Test: Get trend analysis"""
    port = AGENTS["analytics"][1]
    
    result = _get(port, f"/trends/{metric_name}")
    assert result.get("trend_analysis") is not None
    trend = result["trend_analysis"]["trend"]
    print(f"✅ Analytics: Trend analysis - {metric_name}: {trend['trend']} ({trend['change_percentage']}%)")


def test_analytics_export_pdf(analytics_report: str):
    port = AGENTS["analytics"][1]
    result = _post(port, "/export/pdf", {"report_id": analytics_report})
    assert result.get("export") is not None
    print(f"✅ Analytics: PDF exported for {analytics_report}")


def test_analytics_status(analytics_report: str):
    port = AGENTS["analytics"][1]
    result = _get(port, "/status")
    assert result.get("service") == "opena17_Analytics"
    print(f"✅ Analytics: Status - Reports: {result.get('reports_generated')}")


# ============================================================================
# TEST: Agent 18 (Dashboard)
# ============================================================================

def test_dashboard_create_widget(dashboard_widget: str):
    assert dashboard_widget.startswith("WID_")
    print(f"✅ Dashboard: Widget created: {dashboard_widget}")


def test_dashboard_get_widget(dashboard_widget: str):
    port = AGENTS["dashboard"][1]
    result = _get(port, f"/widget/{dashboard_widget}")
    assert result.get("widget") is not None
    print(f"✅ Dashboard: Widget retrieved: {dashboard_widget}")


def test_dashboard_save_layout(dashboard_layout: str):
    assert dashboard_layout.startswith("LAY_")
    print(f"✅ Dashboard: Layout saved: {dashboard_layout}")


def test_dashboard_get_layout(dashboard_layout: str):
    port = AGENTS["dashboard"][1]
    result = _get(port, f"/layout/{dashboard_layout}")
    assert result.get("layout") is not None
    print(f"✅ Dashboard: Layout retrieved: {dashboard_layout}")


def test_dashboard_refresh_realtime(dashboard_widget: str):
    port = AGENTS["dashboard"][1]
    payload = {"widget_ids": [dashboard_widget]}
    result = _post(port, "/refresh/realtime", payload)
    assert result.get("count", 0) >= 1
    print(f"✅ Dashboard: Real-time refresh - {result.get('count')} widgets")


def test_dashboard_status(dashboard_widget: str, dashboard_layout: str):
    port = AGENTS["dashboard"][1]
    result = _get(port, "/status")
    assert result.get("service") == "opena18_Dashboard"
    print(f"✅ Dashboard: Status - Widgets: {result.get('widgets')}, SSE Subscribers: {result.get('sse_subscribers')}")


# ============================================================================
# TEST: Agent 19 (Workflow)
# ============================================================================

def test_workflow_create(workflow_id: str):
    assert workflow_id.startswith("WFW_")
    print(f"✅ Workflow: Workflow created: {workflow_id}")


def test_workflow_get(workflow_id: str):
    port = AGENTS["workflow"][1]
    result = _get(port, f"/workflow/{workflow_id}")
    assert result.get("workflow") is not None
    print(f"✅ Workflow: Workflow retrieved: {workflow_id}")


def test_workflow_execute(workflow_execution_result: dict):
    print(
        "✅ Workflow: Executed: "
        f"{workflow_execution_result['execution_id']} ({workflow_execution_result['status']})"
    )


def test_workflow_status(workflow_id: str, workflow_execution_result: dict):
    port = AGENTS["workflow"][1]
    result = _get(port, f"/workflow/{workflow_id}/status")
    assert result.get("workflow_id") == workflow_id
    assert result.get("total_executions", 0) >= 1
    print(f"✅ Workflow: Status - {result.get('total_executions')} executions")


def test_workflow_set_trigger(workflow_trigger_id: str):
    assert workflow_trigger_id.startswith("TRG_")
    print(f"✅ Workflow: Trigger set: {workflow_trigger_id}")


def test_workflow_list_triggers(workflow_trigger_id: str):
    port = AGENTS["workflow"][1]
    result = _get(port, "/trigger/list")
    assert any(t.get("id") == workflow_trigger_id for t in result.get("triggers", []))
    print(f"✅ Workflow: {result['count']} triggers listed")


def test_workflow_pause(workflow_id: str):
    port = AGENTS["workflow"][1]
    payload = {"status": "paused", "notes": "Maintenance"}
    result = _post(port, f"/workflow/{workflow_id}/pause", payload)
    assert result.get("updated") is True
    print(f"✅ Workflow: Workflow paused: {workflow_id}")


def test_workflow_status_endpoint(workflow_id: str, workflow_trigger_id: str):
    port = AGENTS["workflow"][1]
    result = _get(port, "/status")
    assert result.get("service") == "opena19_Workflow"
    print(f"✅ Workflow: Status - Workflows: {result.get('workflows')}, Triggers: {result.get('triggers')}")
