from subscription import Subscription

# Create a new subscription
subscription = Subscription(user_name="John Doe", plan="basic")

print(subscription)

# Change the subscription plan
subscription.change_plan("premium")

# Calculate the active duration in days
duration = subscription.calculate_active_duration()
print(duration)

# Pause the subscription
subscription.pause()

# Get the current subscription status
status = subscription.get_subscription_status()
print(status)

# Resume the subscription
subscription.resume()

# Calculate the pro-rated cost of the subscription
cost = subscription.calculate_pro_rated_cost()
print(cost)

# Get the current subscription status
status = subscription.get_subscription_status()
print(status)
