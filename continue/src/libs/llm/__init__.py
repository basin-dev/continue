from ...models.main import AbstractModel

class LLM(AbstractModel):
    def complete(self, prompt: str, **kwargs):
        """Return the completion of the text with the given temperature."""
        raise 
    
    def __call__(self, prompt: str, **kwargs):
        return self.complete(prompt, **kwargs)
    
    def fine_tune(self, pairs: list):
        """Fine tune the model on the given prompt/completion pairs."""
        raise NotImplementedError