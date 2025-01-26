import matplotlib
matplotlib.use("Agg")  # Ensure headless
import matplotlib.pyplot as plt
from datetime import datetime
import os

def create_dca_plot(purchase_history, symbol: str, output_dir="charts"):
    """
    Create a line chart with buy points.
    Returns the path to the saved PNG file.
    """
    if not purchase_history:
        return None

    # Sort by date
    purchase_history_sorted = sorted(purchase_history, key=lambda x: x[0])
    dates = [datetime.strptime(x[0], '%Y-%m-%d') for x in purchase_history_sorted]
    prices = [x[1] for x in purchase_history_sorted]

    # Make sure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    filename = f"{symbol}_dca_chart_{dates[0].strftime('%Y%m%d')}_{dates[-1].strftime('%Y%m%d')}.png"
    filepath = os.path.join(output_dir, filename)

    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, marker='o', label='Purchase Price')
    plt.title(f"DCA Purchase Prices for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.legend()

    plt.savefig(filepath, bbox_inches='tight')
    plt.close()

    return filepath
