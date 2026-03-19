class CostEstimator:
    """
    Approximate estimator for observability only.
    Adjust rates later if you change providers/models.
    """

    MODEL_RATES_PER_1K = {
        "llama-3.1-8b-instant": {
            "input": 0.00005,
            "output": 0.00008,
        },
        "default": {
            "input": 0.00005,
            "output": 0.00008,
        },
    }

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    def estimate_cost(self, model_name: str, input_text: str, output_text: str) -> dict:
        rates = self.MODEL_RATES_PER_1K.get(model_name, self.MODEL_RATES_PER_1K["default"])

        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text)

        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        total_cost = input_cost + output_cost

        return {
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_usd": round(total_cost, 8),
        }