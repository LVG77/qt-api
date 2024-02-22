from datetime import datetime, timedelta
from qt import Questrade


def generate_date_pairs(n_pairs:int, time_delta:int = 30, start_date:str = None)->list[tuple]:
    date_pairs = []
    if start_date:
        current_date = start_date
    else:
        current_date = datetime.now()  # Start from the current date

    for _ in range(n_pairs):
        next_date = current_date - timedelta(days=time_delta)
        date_pairs.append((current_date.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d")))
        current_date = next_date - timedelta(days=1)

    return date_pairs


def get_acct_activities(qt: Questrade, acct_no: int, n: int, verbose: bool = True)->list[dict]:
    "Get activities for account `acct_no` for `n` consecutive 30-day periods."
    date_pairs = generate_date_pairs(n_pairs=n)
    activities = []
    for d2,d1 in date_pairs:
        print(f"Getting data for {d1} to {d2} period")
        r = qt.get_activities(acct_no, d1, d2)
        activities.extend(r)
    return activities

