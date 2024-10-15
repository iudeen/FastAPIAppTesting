from datetime import datetime


class Subscription:
    def __init__(self, user_name, plan, start_date=None, end_date=None, cancelled=False, paused=False, paused_at=None,
                 resumed_at=None):
        self.user_name = user_name
        self.plan = plan  # 'basic', 'premium', 'pro'
        self.start_date = start_date if start_date else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.end_date = end_date
        self.cancelled = cancelled
        self.paused = paused
        self.paused_at = paused_at
        self.resumed_at = resumed_at

    def cancel(self):
        """Cancel the subscription."""
        if self.cancelled:
            raise ValueError("Subscription is already cancelled")
        self.end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cancelled = True

    def change_plan(self, new_plan):
        """Change the subscription plan."""
        if self.cancelled:
            raise ValueError("Cannot change the plan of a cancelled subscription")
        self.plan = new_plan

    def calculate_active_duration(self):
        """Calculate the active duration of the subscription."""
        if self.cancelled:
            end_time = datetime.strptime(self.end_date, '%Y-%m-%d %H:%M:%S')
        else:
            end_time = datetime.now()

        start_time = datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S')
        return (end_time - start_time).days

    def pause(self):
        """Pause the subscription."""
        if self.paused:
            raise ValueError("Subscription is already paused")
        if self.cancelled:
            raise ValueError("Cannot pause a cancelled subscription")
        self.paused_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.paused = True

    def resume(self):
        """Resume the subscription."""
        if not self.paused:
            raise ValueError("Subscription is not paused")
        self.resumed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.paused = False

    def get_daily_rate(self):
        """Get the daily rate based on the subscription plan."""
        rates = {'basic': 1.00, 'premium': 2.50, 'pro': 5.00}
        return rates.get(self.plan, 1.00)

    def calculate_pro_rated_cost(self):
        """Calculate the pro-rated subscription cost based on active days."""
        if self.cancelled:
            active_period = datetime.strptime(self.end_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.start_date,
                                                                                                      '%Y-%m-%d %H:%M:%S')
        else:
            active_period = datetime.now() - datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S')

        active_days = active_period.days

        # Adjust active days if the subscription was paused
        if self.paused:
            paused_period = datetime.strptime(self.paused_at, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.start_date,
                                                                                                       '%Y-%m-%d %H:%M:%S')
            active_days -= paused_period.days

        # Daily rate based on plan
        daily_rate = self.get_daily_rate()

        # Pro-rated cost
        return active_days * daily_rate

    def get_subscription_status(self):
        """Get the current status of the subscription."""
        if self.cancelled:
            return f"Subscription is cancelled as of {self.end_date}."
        if self.paused:
            return f"Subscription is paused since {self.paused_at}."
        return f"Subscription is active since {self.start_date}."
