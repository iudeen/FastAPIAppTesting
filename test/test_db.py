import pytest
import sqlite3
from db import create_table, create_subscription, get_subscription_by_id, update_subscription
from subscription import Subscription
from datetime import datetime


# Fixture to create an in-memory database for each test
@pytest.fixture(scope="function")
def db_connection():
    # Create an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    create_table(conn)  # Create the table structure
    yield conn  # Provide the connection to the test
    conn.close()  # Teardown: Close the connection after the test


# Test create_table function (already executed in the fixture)
def test_create_table(db_connection):
    cursor = db_connection.cursor()

    # Check if the table was created by querying for its existence
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions';")
    assert cursor.fetchone() is not None  # Table should exist


# Test create_subscription function
def test_create_subscription(db_connection):
    user_name = "Test User"
    plan = "basic"

    # Create a new subscription
    subscription_id = create_subscription(db_connection, user_name, plan)

    # Verify that the subscription was inserted
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE id=?", (subscription_id,))
    subscription = cursor.fetchone()

    assert subscription is not None
    assert subscription[1] == user_name  # user_name should match
    assert subscription[2] == plan  # plan should match


# Test get_subscription_by_id function
def test_get_subscription_by_id(db_connection):
    user_name = "Test User"
    plan = "basic"

    # Insert a subscription into the test database
    subscription_id = create_subscription(db_connection, user_name, plan)

    # Fetch the subscription by ID
    subscription = get_subscription_by_id(db_connection, subscription_id)

    # Verify the returned subscription object
    assert subscription is not None
    assert subscription.user_name == user_name
    assert subscription.plan == plan


# Test update_subscription function
def test_update_subscription(db_connection):
    user_name = "Test User"
    plan = "basic"

    # Insert a subscription into the test database
    subscription_id = create_subscription(db_connection, user_name, plan)

    # Create a mock subscription object with updated details
    updated_subscription = Subscription(
        user_name="Updated User",
        plan="premium",
        start_date="2023-10-10 10:00:00",
        end_date=None,
        cancelled=False,
        paused=False,
        paused_at=None,
        resumed_at=None
    )

    # Update the subscription in the database
    update_subscription(db_connection, subscription_id, updated_subscription)

    # Fetch the updated subscription
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE id=?", (subscription_id,))
    updated_sub = cursor.fetchone()

    # Verify the subscription details were updated
    assert updated_sub[2] == "premium"


# Test updating subscription after cancellation
def test_update_cancelled_subscription(db_connection):
    user_name = "Test User"
    plan = "basic"

    # Insert a subscription into the test database
    subscription_id = create_subscription(db_connection, user_name, plan)

    # Fetch the subscription and cancel it
    subscription = get_subscription_by_id(db_connection, subscription_id)
    subscription.cancel()

    # Update the cancelled subscription
    update_subscription(db_connection, subscription_id, subscription)

    # Fetch the updated subscription
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE id=?", (subscription_id,))
    updated_sub = cursor.fetchone()

    # Verify the subscription is cancelled
    assert updated_sub[4] is not None  # end_date should be set (indicating cancellation)
    assert updated_sub[5] == 1  # cancelled should be True
