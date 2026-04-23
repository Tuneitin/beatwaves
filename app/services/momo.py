"""
Hubtel Mobile Money service for Ghana (MTN, Vodafone, AirtelTigo).
Docs: https://developers.hubtel.com/docs/collect-money
"""
import httpx
import uuid
from app.core.config import get_settings

settings = get_settings()

HUBTEL_BASE = "https://api.hubtel.com/v1/merchantaccount/merchants"

NETWORK_MAP = {
    "mtn": "MTN",
    "vodafone": "VDF",
    "airteltigo": "ATL",
}

MOCK_MODE = not settings.hubtel_client_id or not settings.hubtel_client_secret


def _auth():
    return (settings.hubtel_client_id, settings.hubtel_client_secret)


def _mock_response(prefix: str, reference: str, description: str = None) -> dict:
    return {
        "status": "success",
        "data": {
            "transactionId": f"{prefix}-{reference}",
            "externalTransactionId": reference,
            "description": description or "Mock payment initiated",
        },
        "_mock": True,
    }


async def request_payment(
    amount: float,
    momo_number: str,
    network: str,
    description: str,
    reference: str = None,
) -> dict:
    """
    Initiate a MoMo collection (charge customer).
    Returns Hubtel response dict.
    In sandbox/dev mode returns a mock success response.
    """
    ref = reference or str(uuid.uuid4())
    network_code = NETWORK_MAP.get(network.lower(), "MTN")

    if MOCK_MODE:
        return _mock_response("mock", ref, description or "Mock payment initiated")

    payload = {
        "Amount": round(amount, 2),
        "Title": settings.app_name,
        "Description": description or "BeatWave payment",
        "PrimaryCallbackUrl": f"{settings.frontend_url}/api/payments/callback",
        "ClientReference": ref,
        "CustomerName": "BeatWave User",
        "CustomerMsisdn": momo_number,
        "Channel": network_code,
    }

    try:
        async with httpx.AsyncClient(auth=_auth(), timeout=30) as client:
            resp = await client.post(
                f"{HUBTEL_BASE}/receive-money",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        return {
            "status": "failed",
            "error": "Hubtel API returned an error",
            "detail": exc.response.text,
            "status_code": exc.response.status_code,
        }
    except httpx.RequestError as exc:
        return {
            "status": "failed",
            "error": str(exc),
        }


async def request_withdrawal(
    amount: float,
    momo_number: str,
    network: str,
    reference: str = None,
) -> dict:
    """
    Send money to artist's MoMo number (withdrawal of royalties).
    """
    ref = reference or str(uuid.uuid4())
    network_code = NETWORK_MAP.get(network.lower(), "MTN")

    if MOCK_MODE:
        return _mock_response("mock-withdraw", ref)

    payload = {
        "RecipientName": "BeatWave Artist",
        "RecipientMsisdn": momo_number,
        "Channel": network_code,
        "Amount": round(amount, 2),
        "PrimaryCallbackUrl": f"{settings.frontend_url}/api/payments/callback",
        "Description": "BeatWave royalty withdrawal",
        "ClientReference": ref,
    }

    try:
        async with httpx.AsyncClient(auth=_auth(), timeout=30) as client:
            resp = await client.post(
                f"{HUBTEL_BASE}/send-money",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        return {
            "status": "failed",
            "error": "Hubtel API returned an error",
            "detail": exc.response.text,
            "status_code": exc.response.status_code,
        }
    except httpx.RequestError as exc:
        return {
            "status": "failed",
            "error": str(exc),
        }
