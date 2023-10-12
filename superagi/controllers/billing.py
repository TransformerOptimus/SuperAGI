from fastapi import APIRouter, HTTPException
import stripe
from superagi.config.config import get_config
from starlette.responses import RedirectResponse
from superagi.helper.auth import get_user_organisation
import datetime

router = APIRouter()

stripe_api_key = get_config('STRIPE_API_KEY')

@router.post("/checkout_session")
def setup_checkout_session():
    stripe.api_key = stripe_api_key
    organisation_id = get_user_organisation()
    customer = stripe.Customer.create(
        name="Taranjot Kaur"
    )
    print("/////////////////////////////////")
    print(customer)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode='setup',
            customer=customer.id,
            billing_address_collection='required',
            metadata={
                "organisation_id": organisation_id,
            },
            currency="usd",
            phone_number_collection={"enabled": False},
            success_url="http://localhost:3000/api/billing/success/{CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/api/billing/cancel"
        )
        return {"url": session.url}
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to create checkout session")

@router.get("/success/{session_id}")
def handle_checkout_success(session_id):
    stripe.api_key = stripe_api_key
    session = stripe.checkout.Session.retrieve(session_id)
    print("-----------------------------------")
    print(session)
    response = RedirectResponse(url="http://localhost:3000/")
    return response

@router.post("/create_product")
def create_product():
    stripe.api_key = stripe_api_key
    print("-------------------------------------")
    product = stripe.Product.create(
        name="Falcon70B, output",
        type="service",
        unit_label=1000,
        active=True,
        metadata={
            "organisation_id": 1,
            "organisation_name": "Default Organisation"
        }
        )
    print("-------------------------------------")
    print(product)
    return product

@router.post("/create_price/{product_id}")
def create_price(product_id):
    stripe.api_key = stripe_api_key
    price = stripe.Price.create(
        unit_amount_decimal=0.5,
        currency="usd",
        recurring={
            "interval": "day",
            "usage_type": "metered",
            "aggregate_usage": "max"
        },
        product=product_id,
        billing_scheme="per_unit",
        transform_quantity={
            "divide_by": 1000,
            "round": "up"
        }
    )
    print("-------------------------------------")
    print(price)
    return price

@router.get("/retrieve_setup_intent/{setup_intent_id}")
def retrieve_setup_intent(setup_intent_id):
    stripe.api_key = stripe_api_key
    setup_intent = stripe.SetupIntent.retrieve(setup_intent_id)
    print("-------------------------------------")
    print(setup_intent)
    return setup_intent

@router.post("/create_subscription/{customer_id}/{price_id}/{payment_id}")
def create_subscription(customer_id,price_id, payment_id):
    stripe.api_key = stripe_api_key
    print("-------------------------------------")
    try:
        subscription = stripe.Subscription.create(
        customer=customer_id,
        items =[{
            "price": price_id
        }],
        collection_method="charge_automatically",
        default_payment_method=payment_id,
        )   
    except Exception as err:
        return err
    return subscription

@router.post("/record_usage/{subscription_item_id}")
def record_usage(subscription_item_id):
    stripe.api_key = stripe_api_key
    usage = stripe.SubscriptionItem.create_usage_record(
        subscription_item_id,
        quantity=6700,
        timestamp=datetime.datetime.now()
    )
    return usage

@router.post("/create/customer_portal")
def create_customer_portal():
    stripe.api_key = stripe_api_key
    stripe.billing_portal.Configuration.create(
        business_profile={
            "headline": "Superagi"
        },
        features=
        {"invoice_history": {"enabled": True},
        "subscription_cancel": {"enabled": True},
        "subscription_pause": {"enabled": True},
        },
    )
    portal = stripe.billing_portal.Session.create(
        customer = "cus_Ony5CKiDQftttn",
        return_url = "http://localhost:3000/api/billing/customer_portal"
    )
    print("-----------------------")
    print(portal)
    return portal.url

# @router.get("/customer_portal")