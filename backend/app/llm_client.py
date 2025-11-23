import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # load .env from backend folder

class LLMClient:
    """
    Clean interface for calling LLMs via Groq.
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "groq")  # default = groq

        if self.provider != "groq":
            raise RuntimeError(f"Unsupported LLM provider: {self.provider}")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in environment variables")

        # create Groq client
        self.client = Groq(api_key=api_key)

        # ✅ use a currently supported model
        # You can change this later if you want another Groq model
        self.model = "llama-3.1-8b-instant"

    async def ask(self, prompt: str) -> str:
        """
        Sends the prompt to the LLM and returns generated text.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful QA expert for GMP batch records.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content
        except Exception as e:
            # helpful error message for debugging
            return f"LLM error: {e}"
