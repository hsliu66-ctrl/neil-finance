from AlgorithmImports import *

class NeilETFAllocation(QCAlgorithm):
    """Illustrative quarterly VT/AGG/GLD portfolio, not investment advice."""
    def initialize(self):
        self.set_start_date(2018, 1, 1)
        self.set_end_date(2025, 12, 31)
        self.set_cash(100000)
        self.targets = {}
        for ticker, weight in (("VT", 0.50), ("AGG", 0.30), ("GLD", 0.20)):
            symbol = self.add_equity(ticker, Resolution.DAILY).symbol
            self.targets[symbol] = weight
        benchmark = next(symbol for symbol in self.targets if symbol.value == "VT")
        self.set_benchmark(benchmark)
        self.schedule.on(
            self.date_rules.month_start(benchmark),
            self.time_rules.after_market_open(benchmark, 30),
            self.quarterly_rebalance
        )

    def quarterly_rebalance(self):
        if self.time.month not in (1, 4, 7, 10):
            return
        if not all(self.securities[s].has_data for s in self.targets):
            return
        for symbol, weight in self.targets.items():
            self.set_holdings(symbol, weight)
