"""
Payment routes for Edge Mode (Stripe integration)
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid

from config import db, logger, STRIPE_API_KEY, SUBSCRIPTION_PRICES
from models.schemas import CreateCheckoutRequest
from utils.auth import get_current_user
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-checkout")
async def create_checkout(request: CreateCheckoutRequest, current_user: dict = Depends(get_current_user)):
    try:
        if request.plan not in SUBSCRIPTION_PRICES:
            raise HTTPException(status_code=400, detail='Invalid subscription plan')
        
        amount = SUBSCRIPTION_PRICES[request.plan]
        
        host_url = request.origin_url
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        success_url = f"{host_url}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{host_url}/profile"
        
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user['id'],
                "email": current_user['email'],
                "username": current_user.get('username'),
                "plan": request.plan
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        transaction_doc = {
            'id': str(uuid.uuid4()),
            'session_id': session.session_id,
            'user_id': current_user['id'],
            'amount': amount,
            'currency': 'usd',
            'plan': request.plan,
            'payment_status': 'pending',
            'status': 'initiated',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {
                "user_id": current_user['id'],
                "email": current_user['email'],
                "plan": request.plan
            }
        }
        await db.payment_transactions.insert_one(transaction_doc)
        
        return {'url': session.url, 'session_id': session.session_id}
    
    except Exception as e:
        logger.error(f"Failed to create checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{session_id}")
async def get_payment_status(session_id: str, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Checking payment status for session: {session_id}")
        
        existing_transaction = await db.payment_transactions.find_one({
            'session_id': session_id,
            'payment_status': 'paid'
        }, {'_id': 0})
        
        if existing_transaction:
            logger.info(f"Transaction already processed and paid for session: {session_id}")
            return {
                'status': 'complete',
                'payment_status': 'paid',
                'already_processed': True
            }
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        logger.info(f"Stripe status for {session_id}: {checkout_status.payment_status}")
        
        await db.payment_transactions.update_one(
            {'session_id': session_id},
            {'$set': {
                'status': checkout_status.status,
                'payment_status': checkout_status.payment_status,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if checkout_status.payment_status == 'paid':
            transaction = await db.payment_transactions.find_one({'session_id': session_id}, {'_id': 0})
            if transaction:
                user_id = transaction.get('metadata', {}).get('user_id')
                if user_id:
                    update_result = await db.users.update_one(
                        {'id': user_id},
                        {'$set': {'subscription_active': True}}
                    )
                    logger.info(f"Activated subscription for user {user_id} - matched: {update_result.matched_count}, modified: {update_result.modified_count}")
                    
                    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'username': 1, 'subscription_active': 1})
                    logger.info(f"User {user.get('username')} subscription_active is now: {user.get('subscription_active')}")
                else:
                    logger.error(f"No user_id found in transaction metadata for session {session_id}")
            else:
                logger.error(f"Transaction not found for session {session_id}")
        
        return {
            'status': checkout_status.status,
            'payment_status': checkout_status.payment_status
        }
    
    except Exception as e:
        logger.error(f"Failed to get payment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Webhook router (needs to be at root level, not /payments)
webhook_router = APIRouter(tags=["Webhooks"])


@webhook_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        await db.payment_transactions.update_one(
            {'session_id': webhook_response.session_id},
            {'$set': {
                'payment_status': webhook_response.payment_status,
                'event_type': webhook_response.event_type,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if webhook_response.payment_status == 'paid':
            user_id = webhook_response.metadata.get('user_id')
            if user_id:
                await db.users.update_one(
                    {'id': user_id},
                    {'$set': {'subscription_active': True}}
                )
        
        return {'status': 'success'}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
