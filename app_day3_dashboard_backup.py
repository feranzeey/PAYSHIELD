
import os
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(
    title="PayShield",
    description="Fintech Site Reliability Engineering Platform",
    version="2.0.0"
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing from .env")

    return psycopg2.connect(DATABASE_URL)


def initialize_database():
    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS payments (
                        reference VARCHAR(40) PRIMARY KEY,
                        amount NUMERIC(12, 2) NOT NULL,
                        currency VARCHAR(3) NOT NULL DEFAULT 'NGN',
                        description VARCHAR(100) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS
                    idx_payments_created_at
                    ON payments (created_at DESC);
                """)
    finally:
        connection.close()


@app.on_event("startup")
def startup_event():
    initialize_database()


# --------------------------------------------------
# PAYMENT REQUEST MODEL
# --------------------------------------------------

class PaymentRequest(BaseModel):
    amount: float = Field(gt=0)
    description: str = Field(min_length=3, max_length=100)
    simulate_failure: bool = False


# --------------------------------------------------
# PROFESSIONAL PAYSHIELD DASHBOARD
# --------------------------------------------------

DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>PayShield | Operations Center</title>

<style>
:root {
    --background: #080d18;
    --panel: #101827;
    --panel-light: #172235;
    --border: #25334a;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --gold: #d6ad60;
    --green: #34d399;
    --red: #fb7185;
    --blue: #60a5fa;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--background);
    color: var(--text);
    font-family: Inter, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif;
}

button, input {
    font: inherit;
}

.layout {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 245px;
    padding: 28px 18px;
    background: #0c1422;
    border-right: 1px solid var(--border);
    flex-shrink: 0;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 8px 32px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    background: rgba(214,173,96,.12);
    border: 1px solid rgba(214,173,96,.35);
    border-radius: 12px;
    color: var(--gold);
    font-size: 23px;
    font-weight: 800;
}

.brand-name {
    font-size: 19px;
    font-weight: 750;
    letter-spacing: -.6px;
}

.brand-name span {
    color: var(--gold);
}

.brand-sub {
    color: var(--muted);
    font-size: 10px;
    margin-top: 4px;
    letter-spacing: 1.2px;
}

.nav-label {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    padding: 15px 12px 10px;
}

.nav-item {
    padding: 12px;
    border-radius: 9px;
    margin-bottom: 5px;
    color: #a8b4c7;
    font-size: 13px;
}

.nav-item.active {
    color: var(--gold);
    background: rgba(214,173,96,.10);
    border: 1px solid rgba(214,173,96,.16);
}

.sidebar-note {
    margin-top: 45px;
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 12px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.7;
}

.sidebar-note strong {
    color: var(--gold);
    display: block;
    margin-bottom: 5px;
}

.main {
    flex: 1;
    min-width: 0;
    padding: 30px 36px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    margin-bottom: 32px;
}

.eyebrow {
    color: var(--gold);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

h1 {
    font-size: 27px;
    margin: 8px 0;
    letter-spacing: -.8px;
}

.subtitle {
    color: var(--muted);
    font-size: 13px;
}

.status {
    display: flex;
    align-items: center;
    gap: 9px;
    background: rgba(52,211,153,.08);
    border: 1px solid rgba(52,211,153,.2);
    padding: 10px 14px;
    border-radius: 30px;
    color: var(--green);
    font-size: 12px;
    white-space: nowrap;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
}

.status.offline {
    color: var(--red);
    background: rgba(251,113,133,.08);
    border-color: rgba(251,113,133,.2);
}

.status.offline .dot {
    background: var(--red);
}

.demo-banner {
    background: rgba(214,173,96,.07);
    border: 1px solid rgba(214,173,96,.2);
    color: #e8c98d;
    padding: 12px 15px;
    border-radius: 9px;
    font-size: 12px;
    margin-bottom: 24px;
}

.metrics {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.metric {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 20px;
    min-width: 0;
}

.metric-label {
    color: var(--muted);
    font-size: 12px;
}

.metric-value {
    font-size: 27px;
    font-weight: 750;
    margin: 15px 0 8px;
    letter-spacing: -.8px;
    overflow-wrap: anywhere;
}

.metric-foot {
    color: var(--muted);
    font-size: 11px;
}

.gold { color: var(--gold); }
.green { color: var(--green); }
.red { color: var(--red); }
.blue { color: var(--blue); }

.content-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(270px, .8fr);
    gap: 18px;
    align-items: start;
}

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 13px;
    overflow: hidden;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 19px 20px;
    border-bottom: 1px solid var(--border);
    gap: 10px;
}

.panel-title {
    font-size: 14px;
    font-weight: 700;
}

.panel-caption {
    color: var(--muted);
    font-size: 11px;
    margin-top: 5px;
}

.refresh-label {
    color: var(--muted);
    font-size: 10px;
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 520px;
}

th {
    text-align: left;
    color: #75849a;
    font-size: 10px;
    letter-spacing: .8px;
    padding: 14px 17px;
    font-weight: 700;
}

td {
    padding: 15px 17px;
    border-top: 1px solid rgba(37,51,74,.7);
    font-size: 11px;
    color: #cbd5e1;
}

.reference {
    color: var(--gold);
    font-weight: 650;
}

.pill {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
}

.pill.success {
    background: rgba(52,211,153,.1);
    color: var(--green);
}

.pill.failed {
    background: rgba(251,113,133,.1);
    color: var(--red);
}

.empty {
    padding: 30px;
    text-align: center;
    color: var(--muted);
    font-size: 12px;
}

.form-body {
    padding: 20px;
}

.field {
    margin-bottom: 17px;
}

.field label {
    display: block;
    color: #aab6c8;
    font-size: 11px;
    margin-bottom: 8px;
}

.field input {
    width: 100%;
    background: #0a1220;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    color: white;
    outline: none;
}

.field input:focus {
    border-color: var(--gold);
}

.checkbox-row {
    display: flex;
    gap: 9px;
    align-items: center;
    color: var(--muted);
    font-size: 11px;
    margin: 5px 0 19px;
}

.checkbox-row input {
    accent-color: var(--gold);
}

.submit {
    width: 100%;
    border: 0;
    background: var(--gold);
    color: #111827;
    padding: 13px;
    border-radius: 8px;
    font-weight: 750;
    cursor: pointer;
}

.submit:hover {
    filter: brightness(1.08);
}

.submit:disabled {
    opacity: .5;
    cursor: wait;
}

.message {
    display: none;
    padding: 11px;
    margin-top: 14px;
    border-radius: 8px;
    font-size: 11px;
    line-height: 1.6;
}

.message.show {
    display: block;
}

.message.success {
    color: var(--green);
    background: rgba(52,211,153,.08);
}

.message.error {
    color: var(--red);
    background: rgba(251,113,133,.08);
}

.system-panel {
    margin-top: 18px;
}

.system-row {
    display: flex;
    justify-content: space-between;
    padding: 15px 19px;
    border-top: 1px solid rgba(37,51,74,.7);
    font-size: 11px;
}

.system-name {
    color: #b7c3d3;
}

.system-state {
    color: var(--green);
    font-weight: 700;
}

.system-state.down {
    color: var(--red);
}

.footer {
    margin-top: 30px;
    color: #64748b;
    font-size: 10px;
    text-align: center;
    line-height: 1.8;
}

@media(max-width: 1050px) {
    .metrics {
        grid-template-columns: repeat(2, 1fr);
    }
    .content-grid {
        grid-template-columns: 1fr;
    }
}

@media(max-width: 700px) {
    .sidebar {
        display: none;
    }
    .main {
        padding: 22px 15px;
    }
    .topbar {
        align-items: flex-start;
        flex-direction: column;
    }
    h1 {
        font-size: 23px;
    }
    .metric {
        padding: 15px;
    }
    .metric-value {
        font-size: 21px;
    }
    .metrics {
        gap: 10px;
    }
}
</style>
</head>

<body>
<div class="layout">

    <aside class="sidebar">
        <div class="brand">
            <div class="brand-icon">P</div>
            <div>
                <div class="brand-name">Pay<span>Shield</span></div>
                <div class="brand-sub">RELIABILITY PLATFORM</div>
            </div>
        </div>

        <div class="nav-label">OPERATIONS</div>
        <div class="nav-item active">◈ &nbsp; Overview</div>
        <div class="nav-item">▤ &nbsp; Transactions</div>
        <div class="nav-item">⌁ &nbsp; Reliability</div>
        <div class="nav-item">◉ &nbsp; Service health</div>

        <div class="nav-label">ENGINEERING</div>
        <div class="nav-item">▧ &nbsp; Infrastructure</div>
        <div class="nav-item">⚑ &nbsp; Incident response</div>

        <div class="sidebar-note">
            <strong>ENGINEERING DEMO</strong>
            PayShield is a simulated fintech reliability environment.
            No real payments are processed.
        </div>
    </aside>

    <main class="main">

        <header class="topbar">
            <div>
                <div class="eyebrow">PAYMENT INFRASTRUCTURE</div>
                <h1>Operations Center</h1>
                <div class="subtitle">
                    Monitor transaction activity and payment service health.
                </div>
            </div>

            <div class="status" id="overall-status">
                <span class="dot"></span>
                <span id="overall-status-text">Checking services...</span>
            </div>
        </header>

        <div class="demo-banner">
            DEMONSTRATION ENVIRONMENT &nbsp;|&nbsp;
            Simulated transactions and operational metrics.
            Not connected to a live payment network.
        </div>

        <section class="metrics">

            <div class="metric">
                <div class="metric-label">Total transactions</div>
                <div class="metric-value gold" id="total-payments">—</div>
                <div class="metric-foot">Recorded payment requests</div>
            </div>

            <div class="metric">
                <div class="metric-label">Successful payments</div>
                <div class="metric-value green" id="successful-payments">—</div>
                <div class="metric-foot">Successfully simulated</div>
            </div>

            <div class="metric">
                <div class="metric-label">Failed payments</div>
                <div class="metric-value red" id="failed-payments">—</div>
                <div class="metric-foot">Failed simulated requests</div>
            </div>

            <div class="metric">
                <div class="metric-label">Payment success rate</div>
                <div class="metric-value blue" id="success-rate">—</div>
                <div class="metric-foot">Successful / total transactions</div>
            </div>

        </section>

        <section class="content-grid">

            <div>
                <div class="panel">
                    <div class="panel-header">
                        <div>
                            <div class="panel-title">Recent transactions</div>
                            <div class="panel-caption">
                                Latest payment records from PostgreSQL
                            </div>
                        </div>
                        <div class="refresh-label">AUTO REFRESH: 10 SEC</div>
                    </div>

                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>REFERENCE</th>
                                    <th>AMOUNT</th>
                                    <th>DESCRIPTION</th>
                                    <th>STATUS</th>
                                </tr>
                            </thead>
                            <tbody id="transaction-table">
                                <tr>
                                    <td colspan="4" class="empty">
                                        Loading transactions...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="panel system-panel">
                    <div class="panel-header">
                        <div>
                            <div class="panel-title">Service health</div>
                            <div class="panel-caption">
                                Application and database connectivity
                            </div>
                        </div>
                    </div>

                    <div class="system-row">
                        <span class="system-name">Payment API</span>
                        <span class="system-state" id="api-state">Checking...</span>
                    </div>

                    <div class="system-row">
                        <span class="system-name">PostgreSQL database</span>
                        <span class="system-state" id="db-state">Checking...</span>
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">Payment simulator</div>
                        <div class="panel-caption">
                            Submit a test transaction
                        </div>
                    </div>
                </div>

                <form class="form-body" id="payment-form">

                    <div class="field">
                        <label for="amount">Payment amount (NGN)</label>
                        <input
                            id="amount"
                            type="number"
                            min="0.01"
                            step="0.01"
                            placeholder="e.g. 50000"
                            required
                        >
                    </div>

                    <div class="field">
                        <label for="description">Transaction description</label>
                        <input
                            id="description"
                            type="text"
                            minlength="3"
                            maxlength="100"
                            placeholder="Test payment"
                            required
                        >
                    </div>

                    <label class="checkbox-row">
                        <input type="checkbox" id="simulate-failure">
                        Simulate a payment failure
                    </label>

                    <button class="submit" id="submit-button" type="submit">
                        Process test payment
                    </button>

                    <div class="message" id="payment-message"></div>

                </form>
            </div>

        </section>

        <div class="footer">
            PAYSHIELD SRE PLATFORM · VERSION 2.0.0<br>
            Built as an engineering portfolio demonstration.
        </div>

    </main>
</div>

<script>
const numberFormat = new Intl.NumberFormat("en-NG");
const nairaFormat = new Intl.NumberFormat("en-NG", {
    style: "currency",
    currency: "NGN",
    maximumFractionDigits: 2
});

function setServiceState(elementId, healthy) {
    const element = document.getElementById(elementId);
    element.textContent = healthy ? "OPERATIONAL" : "UNAVAILABLE";
    element.classList.toggle("down", !healthy);
}

async function loadSummary() {
    try {
        const response = await fetch("/metrics/summary");

        if (!response.ok) {
            throw new Error("Could not load metrics");
        }

        const data = await response.json();

        document.getElementById("total-payments").textContent =
            numberFormat.format(data.total);

        document.getElementById("successful-payments").textContent =
            numberFormat.format(data.successful);

        document.getElementById("failed-payments").textContent =
            numberFormat.format(data.failed);

        document.getElementById("success-rate").textContent =
            data.success_rate + "%";

    } catch (error) {
        console.error(error);
    }
}

async function loadTransactions() {
    const table = document.getElementById("transaction-table");

    try {
        const response = await fetch("/payments");

        if (!response.ok) {
            throw new Error("Could not load transactions");
        }

        const data = await response.json();
        table.replaceChildren();

        if (data.transactions.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 4;
            cell.className = "empty";
            cell.textContent = "No transactions recorded yet.";
            row.appendChild(cell);
            table.appendChild(row);
            return;
        }

        data.transactions.slice(0, 8).forEach(transaction => {
            const row = document.createElement("tr");

            const reference = document.createElement("td");
            reference.className = "reference";
            reference.textContent = transaction.reference;

            const amount = document.createElement("td");
            amount.textContent = nairaFormat.format(
                Number(transaction.amount)
            );

            const description = document.createElement("td");
            description.textContent = transaction.description;

            const statusCell = document.createElement("td");
            const badge = document.createElement("span");
            const isSuccessful = transaction.status === "successful";

            badge.className = "pill " +
                (isSuccessful ? "success" : "failed");

            badge.textContent = transaction.status.toUpperCase();

            statusCell.appendChild(badge);

            row.append(reference, amount, description, statusCell);
            table.appendChild(row);
        });

    } catch (error) {
        table.replaceChildren();
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 4;
        cell.className = "empty";
        cell.textContent = "Unable to retrieve transaction records.";
        row.appendChild(cell);
        table.appendChild(row);
    }
}

async function checkHealth() {
    let apiHealthy = false;
    let databaseHealthy = false;

    try {
        const response = await fetch("/health");
        apiHealthy = response.ok;
    } catch (error) {
        apiHealthy = false;
    }

    try {
        const response = await fetch("/ready");
        databaseHealthy = response.ok;
    } catch (error) {
        databaseHealthy = false;
    }

    setServiceState("api-state", apiHealthy);
    setServiceState("db-state", databaseHealthy);

    const overall = document.getElementById("overall-status");
    const label = document.getElementById("overall-status-text");
    const allHealthy = apiHealthy && databaseHealthy;

    overall.classList.toggle("offline", !allHealthy);
    label.textContent = allHealthy
        ? "All services operational"
        : "Service issue detected";
}

async function refreshDashboard() {
    await Promise.all([
        loadSummary(),
        loadTransactions(),
        checkHealth()
    ]);
}

document.getElementById("payment-form").addEventListener(
    "submit",
    async function(event) {
        event.preventDefault();

        const button = document.getElementById("submit-button");
        const message = document.getElementById("payment-message");

        button.disabled = true;
        button.textContent = "Processing...";
        message.className = "message";
        message.textContent = "";

        const payload = {
            amount: Number(document.getElementById("amount").value),
            description: document.getElementById("description").value,
            simulate_failure:
                document.getElementById("simulate-failure").checked
        };

        try {
            const response = await fetch("/payments", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Payment request failed"
                );
            }

            const transaction = data.transaction;

            message.className = "message show " +
                (transaction.status === "successful" ? "success" : "error");

            message.textContent =
                "Payment " + transaction.status +
                ". Reference: " + transaction.reference;

            document.getElementById("payment-form").reset();

            await refreshDashboard();

        } catch (error) {
            message.className = "message show error";
            message.textContent = error.message;
        } finally {
            button.disabled = false;
            button.textContent = "Process test payment";
        }
    }
);

refreshDashboard();
setInterval(refreshDashboard, 10000);
</script>

</body>
</html>
"""


# --------------------------------------------------
# DASHBOARD ROUTES
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=DASHBOARD)


# --------------------------------------------------
# HEALTH AND READINESS
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "payment-api"
    }


@app.get("/ready")
def ready():
    try:
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
        finally:
            connection.close()

        return {
            "status": "ready",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable"
        )


# --------------------------------------------------
# PAYMENT API
# --------------------------------------------------

@app.post("/payments", status_code=201)
def create_payment(payment: PaymentRequest):
    reference = f"PAY-{uuid4().hex[:12].upper()}"

    status = (
        "failed" if payment.simulate_failure else "successful"
    )

    connection = get_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO payments
                    (reference, amount, currency, description, status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING reference, amount, currency,
                              description, status, created_at;
                    """,
                    (
                        reference,
                        payment.amount,
                        "NGN",
                        payment.description,
                        status
                    )
                )

                transaction = cursor.fetchone()

        return {
            "message": "Payment processed",
            "transaction": transaction
        }

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Payment could not be stored. Database error."
        )

    finally:
        connection.close()


@app.get("/payments")
def get_all_payments():
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT reference, amount, currency,
                       description, status, created_at
                FROM payments
                ORDER BY created_at DESC;
            """)

            records = cursor.fetchall()

        return {
            "total": len(records),
            "transactions": records
        }

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve transactions"
        )

    finally:
        connection.close()


@app.get("/payments/{reference}")
def get_payment(reference: str):
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT reference, amount, currency,
                       description, status, created_at
                FROM payments
                WHERE reference = %s;
                """,
                (reference,)
            )

            transaction = cursor.fetchone()

        if transaction is None:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        return transaction

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve transaction"
        )

    finally:
        connection.close()


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

@app.get("/metrics/summary")
def metrics_summary():
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE status = 'successful'
                    ) AS successful,
                    COUNT(*) FILTER (
                        WHERE status = 'failed'
                    ) AS failed,
                    COALESCE(SUM(amount), 0) AS total_amount
                FROM payments;
            """)

            result = cursor.fetchone()

        total = int(result["total"])
        successful = int(result["successful"])
        failed = int(result["failed"])

        success_rate = (
            round((successful / total) * 100, 2)
            if total > 0 else 0
        )

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "total_amount": float(result["total_amount"]),
            "success_rate": success_rate
        }

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve reliability metrics"
        )

    finally:
        connection.close()
