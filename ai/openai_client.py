from __future__ import annotations

from openai import OpenAI


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    def chat(self, user_message: str, context: str = "") -> str:
        system_prompt = (
            "You are Jackson Siow's personal AI assistant. "
            "Be concise, practical, and action-oriented."
        )
        if context:
            system_prompt += f"\n\nContext:\n{context}"

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or "I couldn't generate a response."
