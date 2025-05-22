import pandas as pd
import random

class PlayerDataLoader:
    def __init__(self, path):
        xls = pd.ExcelFile(path)
        self.data = {
            "Batsman": pd.read_excel(xls, "Batsman").set_index("Player"),
            "Bowlers": pd.read_excel(xls, "Bowlers").set_index("Player"),
            "Wicket Keeper": pd.read_excel(xls, "Wicket Keepers").set_index("Player"),
            "All Rounder": pd.read_excel(xls, "All Rounders").set_index("Player")
        }
        for df in self.data.values():
            if "Nationality" in df.columns:
                df["Nationality"] = df["Nationality"].map({'I': 'India', 'F': 'Foreign'})

    def get(self, player_name):
        for role, df in self.data.items():
            if player_name in df.index:
                row = df.loc[player_name]
                return {
                    "name": player_name,
                    "role": role,
                    "stars": row.get("Stars", 0),
                    "base_price": row.get("Base Price (Cr)", 1),
                    "is_foreign": row.get("Nationality", "India") == "Foreign",
                    "batting_avg": row.get("Average", 30),
                    "strike_rate": row.get("Strike Rates", 100),
                    "wickets": row.get("Wkts", 0),
                    "economy": row.get("Economy", 7)
                }
        return None

class AdvancedBiddingBot:
    def __init__(self, data_path, total_budget=40, foreign_limit=4):
        self.loader = PlayerDataLoader(data_path)
        self.budget = total_budget
        self.foreign_limit = foreign_limit
        self.team = {"Batsman":0, "Bowlers":0, "Wicket Keeper":0, "All Rounder":0, "Foreign":0}
        self.players = []
        self.q_table = {}
        self.alpha = 0.8
        self.gamma = 0.95
        self.epsilon = 0.5
        self.min_epsilon = 0.05
        self.epsilon_decay = 0.9

    def _state(self):
        return (
            min(self.team["Batsman"],3),
            min(self.team["Bowlers"],3),
            1 if self.team["Wicket Keeper"]>0 else 0,
            min(self.team["Foreign"], self.foreign_limit),
            int(self.budget//1)
        )

    def _evaluate_rule(self, player):
        # Base heuristic scoring
        val = (player["stars"] +1)/player["base_price"]
        weights = {"Batsman":1.2,"Bowlers":1.2,"Wicket Keeper":1.5,"All Rounder":1.1}
        val *= weights.get(player["role"],1)
        # stats boost
        if player["role"] in ["Batsman","All Rounder"]:
            val *= (player["batting_avg"]/30)*(player["strike_rate"]/100)
        if player["role"] in ["Bowlers","All Rounder"]:
            val *= ((player["wickets"]+1)/25)*(7/(player["economy"]+1))
        # foreign limit
        if player["is_foreign"] and self.team["Foreign"]>=self.foreign_limit:
            return 0
        return val

    def _action_q(self, state):
        # choose between 'bid' and 'no_bid'
        if state not in self.q_table:
            self.q_table[state] = {'bid':1.0, 'no_bid':1.0}
        if random.random() < self.epsilon:
            return random.choice(['bid','no_bid'])
        return max(self.q_table[state], key=self.q_table[state].get)

    def _update_q(self, old_state, action, reward, new_state):
        if new_state not in self.q_table:
            self.q_table[new_state] = {'bid':1.0, 'no_bid':1.0}
        old_value = self.q_table[old_state][action]
        future = max(self.q_table[new_state].values())
        self.q_table[old_state][action] = old_value + self.alpha*(reward + self.gamma*future - old_value)

    def should_bid(self, name, current_bid, next_bid):
        player = self.loader.get(name)
        if not player or next_bid>self.budget:
            return False
        # Must-have rule
        if (player['role']=='Wicket Keeper' and self.team['Wicket Keeper']==0) or \
           (player['role']=='Batsman' and self.team['Batsman']<3) or \
           (player['role']=='Bowlers' and self.team['Bowlers']<3):
            return True
        # heuristic threshold
        score = self._evaluate_rule(player)
        rule_decision = score>1.0 and next_bid<=player['base_price']*1.5
        # Q-learning fallback
        state = self._state()
        action = self._action_q(state)
        decision = rule_decision or (action=='bid')
        # record for update
        self._last = (state, action, player, next_bid)
        return decision

    def update(self, name, price):
        player = self.loader.get(name)
        # update team
        self.budget -= price
        self.players.append(player)
        self.team[player['role']] +=1
        if player['is_foreign']:
            self.team['Foreign']+=1
        # Q-learning
        old_state, action, _, bid = self._last
        new_state = self._state()
        reward = player['stars']*10 - bid
        self._update_q(old_state, action, reward, new_state)
        self.epsilon = max(self.min_epsilon, self.epsilon*self.epsilon_decay)

data_path = "/kaggle/input/datasetfile/FINAL DATASET.xlsx"
bot = AdvancedBiddingBot(data_path)
players = ["MP Stoinis","AR Patel","R Ashwin","H Klaasen"]
for name in players:
    curr = random.uniform(0.5,2)
    nxt = min(2, curr+0.1)
    if bot.should_bid(name, curr, nxt):
        bot.update(name, nxt)
        print(f"AdvancedBot bids on {name} at {nxt:.2f} Cr")
    else:
        print(f"AdvancedBot skips {name}")
print("Final team:", bot.players)
print("Remaining budget:", bot.budget)