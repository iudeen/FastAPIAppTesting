import sqlite3
from contextlib import asynccontextmanager
from typing import List, Annotated

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from db import get_db, create_table, create_subscription, get_subscription_by_id, update_subscription, \
    get_all_subscriptions


# Create the table on startup using FastAPI lifecycle event
@asynccontextmanager
async def lifespan(app: FastAPI): # pragma: no cover
    conn = sqlite3.connect("subscriptions.db")
    create_table(conn)
    conn.close()
    yield


app = FastAPI(lifespan=lifespan)


# Pydantic models
class SubscriptionCreate(BaseModel):
    user_name: str
    plan: str


class SubscriptionUpdatePlan(BaseModel):
    plan: str


class SubscriptionResponse(BaseModel):
    id: int
    user_name: str
    plan: str
    start_date: str
    end_date: str | None = None
    cancelled: bool
    paused: bool
    paused_at: str | None = None
    resumed_at: str | None = None


SessionDep = Annotated[sqlite3.Connection, Depends(get_db)]


# Route to create a subscription
@app.post("/subscriptions/", response_model=SubscriptionResponse)
def create_subscription_route(subscription: SubscriptionCreate, db: SessionDep):
    subscription_id = create_subscription(db, subscription.user_name, subscription.plan)
    created_subscription = get_subscription_by_id(db, subscription_id)

    return SubscriptionResponse(
        id=subscription_id,
        user_name=created_subscription.user_name,
        plan=created_subscription.plan,
        start_date=created_subscription.start_date,
        end_date=created_subscription.end_date,
        cancelled=created_subscription.cancelled,
        paused=created_subscription.paused,
        paused_at=created_subscription.paused_at,
        resumed_at=created_subscription.resumed_at
    )


# Route to update a subscription plan
@app.put("/subscriptions/{subscription_id}/plan", response_model=SubscriptionResponse)
def update_subscription_plan_route(subscription_id: int, update_data: SubscriptionUpdatePlan,
                                   db: SessionDep):
    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.change_plan(update_data.plan)
    update_subscription(db, subscription_id, subscription)

    updated_subscription = get_subscription_by_id(db, subscription_id)

    return SubscriptionResponse(
        id=subscription_id,
        user_name=updated_subscription.user_name,
        plan=updated_subscription.plan,
        start_date=updated_subscription.start_date,
        end_date=updated_subscription.end_date,
        cancelled=updated_subscription.cancelled,
        paused=updated_subscription.paused,
        paused_at=updated_subscription.paused_at,
        resumed_at=updated_subscription.resumed_at
    )


# Route to pause a subscription
@app.post("/subscriptions/{subscription_id}/pause", response_model=SubscriptionResponse)
def pause_subscription_route(subscription_id: int, db: SessionDep):
    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.pause()
    update_subscription(db, subscription_id, subscription)

    paused_subscription = get_subscription_by_id(db, subscription_id)

    return SubscriptionResponse(
        id=subscription_id,
        user_name=paused_subscription.user_name,
        plan=paused_subscription.plan,
        start_date=paused_subscription.start_date,
        end_date=paused_subscription.end_date,
        cancelled=paused_subscription.cancelled,
        paused=paused_subscription.paused,
        paused_at=paused_subscription.paused_at,
        resumed_at=paused_subscription.resumed_at
    )


# Route to resume a subscription
@app.post("/subscriptions/{subscription_id}/resume", response_model=SubscriptionResponse)
def resume_subscription_route(subscription_id: int, db: SessionDep):
    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.resume()
    update_subscription(db, subscription_id, subscription)

    resumed_subscription = get_subscription_by_id(db, subscription_id)

    return SubscriptionResponse(
        id=subscription_id,
        user_name=resumed_subscription.user_name,
        plan=resumed_subscription.plan,
        start_date=resumed_subscription.start_date,
        end_date=resumed_subscription.end_date,
        cancelled=resumed_subscription.cancelled,
        paused=resumed_subscription.paused,
        paused_at=resumed_subscription.paused_at,
        resumed_at=resumed_subscription.resumed_at
    )


# Route to get all subscriptions
@app.get("/subscriptions/", response_model=List[SubscriptionResponse])
def get_all_subscriptions_route(db: SessionDep):
    subscriptions = get_all_subscriptions(db)

    return [
        SubscriptionResponse(
            id=sub[0],
            user_name=sub[1],
            plan=sub[2],
            start_date=sub[3],
            end_date=sub[4],
            cancelled=bool(sub[5]),
            paused=bool(sub[6]),
            paused_at=sub[7],
            resumed_at=sub[8]
        )
        for sub in subscriptions
    ]
