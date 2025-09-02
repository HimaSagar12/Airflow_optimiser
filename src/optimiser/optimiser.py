from src.horizon.horizon import HorizonLLMClient

class Optimiser:
    def __init__(self, code):
        self.code = code
        self.llm_client = HorizonLLMClient()

    def suggest_optimisations(self):
        response = self.llm_client.get_chat_response(
            user_msg=f"""Please analyze the following Python code, which is part of an Airflow DAG, and suggest optimizations.
Focus on parallelization, reducing time and space complexity.
Provide the optimized code.

```python
{self.code}
```"""
        )
        return response["model_answer"]
