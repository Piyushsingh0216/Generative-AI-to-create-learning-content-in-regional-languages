import json
import re
from typing import Dict, List

from openai import OpenAI

from app.core.config import settings
from app.utils.exceptions import AIServiceError


# ====== API KEY PLACEHOLDER ======
# OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
# =================================


class AIService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model

    @staticmethod
    def _trim_text(text: str, max_chars: int = 50000) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n\n[Content truncated for token limits.]"

    @staticmethod
    def _fallback_summary(text: str) -> Dict[str, List[str] | str]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        short_summary = " ".join(sentences[:2]) or "Summary could not be generated from empty input."
        bullet_points = sentences[:5] or ["No key points found."]
        return {"short_summary": short_summary, "bullet_points": bullet_points}

    @staticmethod
    def _fallback_questions(text: str) -> Dict[str, List]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        base = sentences[:5] if sentences else ["the main concept in this document"]
        short_answer_questions = [
            f"Explain: {item[:120]}?" if not item.endswith("?") else item for item in base
        ]
        while len(short_answer_questions) < 5:
            short_answer_questions.append(
                f"What is an important learning point #{len(short_answer_questions) + 1}?"
            )

        mcqs = []
        for idx in range(5):
            prompt = base[idx % len(base)]
            mcqs.append(
                {
                    "question": f"What is the best interpretation of: '{prompt[:70]}'?",
                    "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
                    "answer": "Concept A",
                }
            )
        return {"short_answer_questions": short_answer_questions[:5], "mcqs": mcqs[:5]}

    def _extract_json(self, content: str) -> Dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                raise AIServiceError("AI response did not contain valid JSON.")
            return json.loads(match.group(0))

    def generate_summary(self, text: str) -> Dict[str, List[str] | str]:
        text = self._trim_text(text)
        if not self.client:
            return self._fallback_summary(text)

        # If text is too long, split into chunks and summarize each, then combine
        max_chunk_size = 40000  # Leave room for prompt
        if len(text) > max_chunk_size:
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            summaries = []
            for chunk in chunks[:5]:  # Limit to 5 chunks to avoid too many API calls
                try:
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        temperature=0.2,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are an educational summarizer. Return strict JSON with keys "
                                    "'short_summary' (string) and 'bullet_points' (array of strings)."
                                ),
                            },
                            {"role": "user", "content": f"Summarize this part of the learning content:\n{chunk}"},
                        ],
                        response_format={"type": "json_object"},
                    )
                    content = completion.choices[0].message.content or "{}"
                    data = self._extract_json(content)
                    summaries.append(data)
                except Exception:
                    continue
            
            # Combine summaries
            if summaries:
                combined_text = " ".join([s.get("short_summary", "") for s in summaries])
                all_bullets = []
                for s in summaries:
                    all_bullets.extend(s.get("bullet_points", []))
                
                # Summarize the combined summaries
                try:
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        temperature=0.2,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are an educational summarizer. Combine these partial summaries into one cohesive summary. "
                                    "Return strict JSON with keys 'short_summary' (string) and 'bullet_points' (array of strings)."
                                ),
                            },
                            {"role": "user", "content": f"Combined partial summaries:\n{combined_text}\n\nAll bullet points:\n{' '.join(all_bullets)}"},
                        ],
                        response_format={"type": "json_object"},
                    )
                    content = completion.choices[0].message.content or "{}"
                    data = self._extract_json(content)
                    return {
                        "short_summary": str(data.get("short_summary", "")),
                        "bullet_points": [str(item) for item in data.get("bullet_points", [])][:8],
                    }
                except Exception:
                    # Fallback: use first summary
                    data = summaries[0]
                    return {
                        "short_summary": str(data.get("short_summary", "")),
                        "bullet_points": [str(item) for item in data.get("bullet_points", [])][:8],
                    }
            else:
                return self._fallback_summary(text)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an educational summarizer. Return strict JSON with keys "
                            "'short_summary' (string) and 'bullet_points' (array of strings)."
                        ),
                    },
                    {"role": "user", "content": f"Summarize this learning content:\n{text}"},
                ],
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content or "{}"
            data = self._extract_json(content)
            return {
                "short_summary": str(data.get("short_summary", "")),
                "bullet_points": [str(item) for item in data.get("bullet_points", [])][:8],
            }
        except Exception as exc:
            raise AIServiceError(f"Summary generation failed: {exc}") from exc

    def generate_questions(self, text: str) -> Dict[str, List]:
        text = self._trim_text(text)
        if not self.client:
            return self._fallback_questions(text)

        # If text is too long, use a representative sample
        max_chunk_size = 40000
        if len(text) > max_chunk_size:
            # Take first chunk and a sample from middle and end
            chunk1 = text[:max_chunk_size//2]
            chunk2 = text[len(text)//2:len(text)//2 + max_chunk_size//4]
            chunk3 = text[-max_chunk_size//4:]
            text = chunk1 + "\n\n" + chunk2 + "\n\n" + chunk3

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return strict JSON with keys: short_answer_questions (array of 5 strings), "
                            "mcqs (array of 5 objects). Each mcq object must have question, options (4 strings), answer."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Generate 5 short-answer questions and 5 MCQs from this content:\n"
                            f"{text}"
                        ),
                    },
                ],
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content or "{}"
            data = self._extract_json(content)
            short_questions = [str(item) for item in data.get("short_answer_questions", [])][:5]
            while len(short_questions) < 5:
                short_questions.append(
                    f"What is an important concept in section {len(short_questions) + 1}?"
                )
            mcqs = data.get("mcqs", [])[:5]
            validated_mcqs = []
            for item in mcqs:
                options = [str(opt) for opt in item.get("options", [])][:4]
                if len(options) < 4:
                    options = options + ["Option A", "Option B", "Option C", "Option D"]
                    options = options[:4]
                validated_mcqs.append(
                    {
                        "question": str(item.get("question", "")),
                        "options": options,
                        "answer": str(item.get("answer", options[0])),
                    }
                )
            while len(validated_mcqs) < 5:
                validated_mcqs.append(
                    {
                        "question": f"Placeholder MCQ {len(validated_mcqs) + 1}",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "answer": "Option A",
                    }
                )
            return {"short_answer_questions": short_questions, "mcqs": validated_mcqs}
        except Exception as exc:
            raise AIServiceError(f"Question generation failed: {exc}") from exc

    def chat_with_context(self, message: str, context_text: str, history: List[Dict[str, str]]) -> str:
        context_text = self._trim_text(context_text, 30000)
        if not self.client:
            # Lightweight fallback: return sentences that contain message keywords.
            keywords = [word.lower() for word in re.findall(r"[A-Za-z]{4,}", message)]
            ranked = []
            for sentence in re.split(r"(?<=[.!?])\s+", context_text):
                score = sum(1 for kw in keywords if kw in sentence.lower())
                if score > 0:
                    ranked.append((score, sentence.strip()))
            ranked.sort(key=lambda x: x[0], reverse=True)
            if ranked:
                return " ".join(item[1] for item in ranked[:3])
            return "I could not find a clear answer in the uploaded document context."

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a context-aware tutor. Use ONLY the provided context. "
                        "If information is missing, explicitly say it is not present in context."
                    ),
                },
                {"role": "system", "content": f"Context:\n{context_text}"},
            ]
            for item in history[-6:]:
                role = item.get("role", "user")
                content = item.get("content", "")
                if role in {"system", "assistant", "user"} and content:
                    messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": message})
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=messages,
            )
            return completion.choices[0].message.content or "No response from model."
        except Exception as exc:
            raise AIServiceError(f"Chatbot response generation failed: {exc}") from exc


ai_service = AIService()
