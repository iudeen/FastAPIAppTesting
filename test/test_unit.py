import pytest
from datetime import datetime, timedelta
from subscription import Subscription  # Assuming your code is in a file named `subscription.py`


# Fixture to create a fresh subscription for each test
@pytest.fixture
def subscription():
    return Subscription(user_name="Test User", plan="basic")


# Test creating a new subscription
def test_subscription_creation(subscription):
    assert subscription.user_name == "Test User"
    assert subscription.plan == "basic"
    assert not subscription.cancelled
    assert not subscription.paused
    assert subscription.end_date is None
    assert subscription.paused_at is None
    assert subscription.resumed_at is None


# Test cancelling a subscription
def test_cancel_subscription(subscription):
    subscription.cancel()
    assert subscription.cancelled
    assert subscription.end_date is not None
    with pytest.raises(ValueError, match="Subscription is already cancelled"):
        subscription.cancel()  # Should raise error when canceling again


# Test changing the subscription plan
def test_change_plan(subscription):
    subscription.change_plan("premium")
    assert subscription.plan == "premium"

    # Cannot change the plan of a cancelled subscription
    subscription.cancel()
    with pytest.raises(ValueError, match="Cannot change the plan of a cancelled subscription"):
        subscription.change_plan("pro")


# Test calculating the active duration (no cancellation)
def test_calculate_active_duration(subscription):
    subscription.start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    assert subscription.calculate_active_duration() == 10


# Test calculating active duration after cancellation
def test_calculate_active_duration_after_cancellation(subscription):
    subscription.start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
    subscription.cancel()
    assert subscription.calculate_active_duration() == 5


# Test pausing and resuming the subscription
def test_pause_resume_subscription(subscription):
    subscription.pause()
    assert subscription.paused
    assert subscription.paused_at is not None

    with pytest.raises(ValueError, match="Subscription is already paused"):
        subscription.pause()

    subscription.resume()
    assert not subscription.paused
    assert subscription.resumed_at is not None

    with pytest.raises(ValueError, match="Subscription is not paused"):
        subscription.resume()


# Test pausing a cancelled subscription
def test_pause_cancelled_subscription(subscription):
    subscription.cancel()
    with pytest.raises(ValueError, match="Cannot pause a cancelled subscription"):
        subscription.pause()


# Test calculating the pro-rated cost
def test_calculate_pro_rated_cost(subscription):
    subscription.start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    assert subscription.calculate_pro_rated_cost() == 10.00  # 10 days at $1/day (basic plan)


# Test calculating the pro-rated cost with pause
def test_calculate_pro_rated_cost_with_pause(subscription):
    subscription.start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    subscription.pause()
    subscription.paused_at = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
    assert subscription.calculate_pro_rated_cost() == 5.00  # 5 active days before the pause


def test_calculate_pro_rated_cost_cancelled(subscription):
    subscription.start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    subscription.cancel()
    assert subscription.calculate_pro_rated_cost() == 10.00  # 5 active days before the pause

# Test get_subscription_status
def test_get_subscription_status(subscription):
    status = subscription.get_subscription_status()
    assert "active" in status

    subscription.pause()
    status = subscription.get_subscription_status()
    assert "paused" in status

    subscription.resume()
    status = subscription.get_subscription_status()
    assert "active" in status

    subscription.cancel()
    status = subscription.get_subscription_status()
    assert "cancelled" in status
