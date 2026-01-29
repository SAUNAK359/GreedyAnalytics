from typing import Dict, Any, Optional

import os


def _get_keys(context: Dict[str, Any] | None) -> Dict[str, str]:
    context = context or {}
    return {
        "gemini": context.get("gemini_api_key") or os.getenv("GEMINI_API_KEY", ""),
        "openai": context.get("openai_api_key") or os.getenv("OPENAI_API_KEY", ""),
    }


def run_llm(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    keys = _get_keys(context)

    if keys["gemini"]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=keys["gemini"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return {"text": response.text, "provider": "gemini"}
        except Exception as exc:
            return {"text": f"Gemini error: {exc}", "provider": "gemini"}

    if keys["openai"]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=keys["openai"])
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            text = response.choices[0].message.content
            return {"text": text, "provider": "openai"}
        except Exception as exc:
            return {"text": f"OpenAI error: {exc}", "provider": "openai"}

    return {
        "text": "Mock Gemini response - API key not configured",
        "provider": "mock",
    }
