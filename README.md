
# Advanced Auction Bot 🤖

An AI-driven auction bot that combines **rule-based heuristics** with **Q-learning** to build an optimal cricket squad within a budget. It leverages player stats (stars, averages, economy, etc.) and learns over time which bids pay off.

## Features

- **Hybrid Decision Logic**  
  - **Must-have rules** to guarantee critical roles (Wicket Keeper, minimum Batsmen/Bowlers).  
  - **Heuristic scoring** based on stars, base price, batting & bowling stats.  
  - **Q-learning fallback** (ε-greedy) to explore borderline bids and improve via rewards.

- **Budget & Foreign Constraints**  
  Ensures bids don’t exceed remaining budget and enforces a max of 4 foreign players.

- **Self-updating Q-Table**  
  Learns from wins/losses, decays exploration rate, and fine-tunes strategy over multiple auctions.

- **Modular Data Loader**  
  Reads stats from an Excel file organized into “Batsman”, “Bowlers”, “Wicket Keepers”, and “All Rounders” sheets.

---

## Installation & Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/sarthakv162/Advanced-Auction-Bot.git
   cd Advanced-Auction-Bot

2. **Create & activate a virtual environment** (recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install pandas openpyxl
   ```

4. **Prepare your dataset**
   Place `FINAL DATASET.xlsx` under `data/` (or update the `data_path` in your script):

   ```
   data/
   └── FINAL DATASET.xlsx
   ```

---

## ▶️ Usage

In your Python code (e.g. `BiddingBot.py`), initialize and run:

```python
from advanced_bidding_bot import AdvancedBiddingBot
import random

data_path = "data/FINAL DATASET.xlsx"
bot = AdvancedBiddingBot(data_path)

players_to_auction = ["MP Stoinis", "AR Patel", "R Ashwin", "H Klaasen"]
for name in players_to_auction:
    current_bid = random.uniform(0.5, 2)
    next_bid    = min(2, current_bid + 0.1)
    if bot.should_bid(name, current_bid, next_bid):
        bot.update(name, next_bid)
        print(f"AdvancedBot bids on {name} at {next_bid:.2f} Cr")
    else:
        print(f"AdvancedBot skips {name}")

print("Final team:", [p["name"] for p in bot.players])
print("Remaining budget:", bot.budget)
```

---

## ⚙️ Configuration & Hyperparameters

Edit these in `AdvancedBiddingBot.__init__()` as needed:

* `total_budget` (default: 40)

* `foreign_limit` (default: 4)

* **Q-learning**

  * `alpha` (learning rate)
  * `gamma` (discount factor)
  * `epsilon` (initial exploration)
  * `epsilon_decay` & `min_epsilon`

* **Heuristic threshold** (in `should_bid` method):

  ```python
  score > 1.0 and next_bid <= player["base_price"] * 1.5
  ```

---

## 🧪 Evaluation

To measure performance:

1. Simulate **N** auctions against:

   * Random bidders
   * Pure rule-based bot
   * Human-defined thresholds

2. Track metrics:

   * **Total team stars**
   * **Budget utilization**
   * **Role completion**
   * **Foreign slots used**

---

## Contributing

1. Fork it
2. Create a feature branch (`git checkout -b feature/...`)
3. Commit your changes (`git commit -m "Add ..."`)
4. Push (`git push origin feature/...`) & open a PR

---
## Author

[Sarthak Verma](https://github.com/sarthakv162) · [LinkedIn](https://www.linkedin.com/in/sarthak-verma-6002001b4/)
