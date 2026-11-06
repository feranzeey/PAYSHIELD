
import os
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(
    title="PayShield",
    description="Fintech Site Reliability Engineering Platform",
    version="1.0.0"
)


class PaymentRequest(BaseModel):
    amount: float = Field(gt=0, description="Payment amount in naira")
    description: str = Field(min_length=3, max_length=100)
    simulate_failure: bool = False


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
    finally:
        connection.close()


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/")
def home():
    return {
        "project": "PayShield",
        "message": "Payment reliability platform is running",
        "status": "operational"
    }


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


@app.post("/payments", status_code=201)
def create_payment(payment: PaymentRequest):
    reference = f"PAY-{uuid4().hex[:12].upper()}"

    status = "failed" if payment.simulate_failure else "successful"

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

    finally:
        connection.close()
