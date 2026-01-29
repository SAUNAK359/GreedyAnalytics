class CostController:
    def __init__(self, budget_tokens: int = 100000):
        self.budget_tokens = budget_tokens
        self.used_tokens = 0

    def can_spend(self, tokens: int) -> bool:
        return self.used_tokens + tokens <= self.budget_tokens

    def spend(self, tokens: int) -> None:
        if self.can_spend(tokens):
            self.used_tokens += tokens
