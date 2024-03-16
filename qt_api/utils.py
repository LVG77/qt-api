from datetime import datetime, timedelta
from qt_api.qt import Questrade



def generate_date_pairs(n_pairs:int, time_delta:int = 30, start_date:str = None)->list[tuple]:
    """
    Generate date pairs based on the given number of pairs, time delta, and start date.
    
    Args:
        n_pairs (int): The number of date pairs to generate.
        time_delta (int, optional): The time difference in days between each pair. Defaults to 30.
        start_date (str, optional): The start date for generating the pairs. Defaults to None.
    
    Returns:
        list[tuple]: A list of tuples containing date pairs in the format (current_date, next_date).
    """
    date_pairs = []
    if start_date:
        current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
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
