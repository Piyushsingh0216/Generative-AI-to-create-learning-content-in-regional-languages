from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Iterable, Sequence

from sqlalchemy.orm import Session

from app.models.weak_word import WeakWord
from app.schemas.lesson import LessonDifficulty, LessonQuestion


LESSON_SIZE = 5
DIFFICULTY_ORDER: list[LessonDifficulty] = ["easy", "medium", "hard"]


class SmartLearningService:
    def determine_difficulty(
        self,
        level: int,
        weak_words: Sequence[WeakWord],
        recent_accuracies: Sequence[float],
    ) -> LessonDifficulty:
        base = self._difficulty_from_level(level)
        weak_pressure = sum(min(item.incorrect_count, 3) for item in self.rank_weak_words(weak_words)[:5])
        recent_accuracy = mean(recent_accuracies) if recent_accuracies else None

        # Keep this simple and predictable: use level as base, then nudge by performance.
        if (recent_accuracy is not None and recent_accuracy >= 0.8 and weak_pressure <= 3):
            return self._shift_difficulty(base, +1)
        if (recent_accuracy is not None and recent_accuracy <= 0.5) or weak_pressure >= 8:
            return self._shift_difficulty(base, -1)
        return base

    def select_personalized_questions(
        self,
        question_bank: Sequence[LessonQuestion],
        target_difficulty: LessonDifficulty,
        weak_words: Sequence[WeakWord],
        lesson_size: int = LESSON_SIZE,
    ) -> list[LessonQuestion]:
        if not question_bank:
            return []

        bank_by_id = {question.id: question for question in question_bank}

        ranked_weak_question_ids = [
            item.question_id for item in self.rank_weak_words(weak_words) if item.question_id in bank_by_id
        ]
        review_question_ids = ranked_weak_question_ids[: min(2, len(ranked_weak_question_ids))]

        target_pool = [question for question in question_bank if question.difficulty == target_difficulty]
        if len(target_pool) < lesson_size:
            for neighbor in self._neighbor_difficulties(target_difficulty):
                if len(target_pool) >= lesson_size:
                    break
                target_pool.extend([q for q in question_bank if q.difficulty == neighbor])

        unique_target_pool = self._unique_by_id(target_pool)
        base_slots = max(lesson_size - len(review_question_ids), 0)

        selected_base = [
            question
            for question in unique_target_pool
            if question.id not in set(review_question_ids)
        ][:base_slots]

        if len(selected_base) < base_slots:
            fallback = [
                question
                for question in question_bank
                if question.id not in {item.id for item in selected_base}
                and question.id not in set(review_question_ids)
            ]
            selected_base.extend(fallback[: base_slots - len(selected_base)])

        review_questions = [
            bank_by_id[question_id].model_copy(update={"is_review": True})
            for question_id in review_question_ids
        ]
        normalized_base = [question.model_copy(update={"is_review": False}) for question in selected_base]

        assembled = self._interleave_review_questions(normalized_base, review_questions, lesson_size)
        if len(assembled) < lesson_size:
            selected_ids = {item.id for item in assembled}
            fillers = [
                question.model_copy(update={"is_review": False})
                for question in question_bank
                if question.id not in selected_ids
            ]
            assembled.extend(fillers[: lesson_size - len(assembled)])

        return assembled[:lesson_size]

    def evaluate_submissions(
        self,
        question_by_id: dict[str, LessonQuestion],
        answers: dict[str, str],
    ) -> tuple[int, list[tuple[LessonQuestion, bool]]]:
        evaluated: list[tuple[LessonQuestion, bool]] = []
        correct_count = 0

        for question_id, answer in answers.items():
            question = question_by_id.get(question_id)
            if not question:
                continue
            is_correct = self._normalize(answer) == self._normalize(question.answer)
            if is_correct:
                correct_count += 1
            evaluated.append((question, is_correct))

        return correct_count, evaluated

    def track_weak_words(
        self,
        db: Session,
        user_id: int,
        language_code: str,
        evaluated_answers: Iterable[tuple[LessonQuestion, bool]],
        attempted_at: datetime,
    ) -> list[str]:
        evaluated_list = list(evaluated_answers)
        if not evaluated_list:
            return []

        question_ids = [question.id for question, _ in evaluated_list]
        existing_rows = (
            db.query(WeakWord)
            .filter(
                WeakWord.user_id == user_id,
                WeakWord.language_code == language_code,
                WeakWord.question_id.in_(question_ids),
            )
            .all()
        )
        weak_word_by_question_id = {item.question_id: item for item in existing_rows}

        incorrect_focus_words: list[str] = []
        for question, is_correct in evaluated_list:
            if is_correct and question.id not in weak_word_by_question_id:
                continue

            record = weak_word_by_question_id.get(question.id)
            if not record:
                record = WeakWord(
                    user_id=user_id,
                    language_code=language_code,
                    question_id=question.id,
                    focus_text=(question.focus_text or question.prompt)[:255],
                    incorrect_count=0,
                )
                db.add(record)
                weak_word_by_question_id[question.id] = record

            record.focus_text = (question.focus_text or question.prompt)[:255]
            record.last_attempted_at = attempted_at

            if not is_correct:
                record.incorrect_count += 1
                record.last_incorrect_at = attempted_at
                incorrect_focus_words.append(record.focus_text)

        return list(dict.fromkeys(incorrect_focus_words))

    @staticmethod
    def rank_weak_words(weak_words: Sequence[WeakWord]) -> list[WeakWord]:
        def _sort_datetime(value: datetime | None) -> datetime:
            if value is None:
                return datetime.min
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            return value

        return sorted(
            [item for item in weak_words if item.incorrect_count > 0],
            key=lambda item: (
                item.incorrect_count,
                _sort_datetime(item.last_incorrect_at),
                _sort_datetime(item.updated_at),
            ),
            reverse=True,
        )

    @staticmethod
    def _difficulty_from_level(level: int) -> LessonDifficulty:
        if level <= 1:
            return "easy"
        if level == 2:
            return "medium"
        return "hard"

    def _shift_difficulty(self, value: LessonDifficulty, step: int) -> LessonDifficulty:
        idx = DIFFICULTY_ORDER.index(value)
        new_idx = min(max(idx + step, 0), len(DIFFICULTY_ORDER) - 1)
        return DIFFICULTY_ORDER[new_idx]

    def _neighbor_difficulties(self, value: LessonDifficulty) -> list[LessonDifficulty]:
        idx = DIFFICULTY_ORDER.index(value)
        neighbors: list[LessonDifficulty] = []
        if idx - 1 >= 0:
            neighbors.append(DIFFICULTY_ORDER[idx - 1])
        if idx + 1 < len(DIFFICULTY_ORDER):
            neighbors.append(DIFFICULTY_ORDER[idx + 1])
        return neighbors

    @staticmethod
    def _normalize(value: str | None) -> str:
        return (value or "").strip().casefold()

    @staticmethod
    def _unique_by_id(questions: Sequence[LessonQuestion]) -> list[LessonQuestion]:
        seen: set[str] = set()
        result: list[LessonQuestion] = []
        for question in questions:
            if question.id in seen:
                continue
            seen.add(question.id)
            result.append(question)
        return result

    @staticmethod
    def _interleave_review_questions(
        base_questions: list[LessonQuestion],
        review_questions: list[LessonQuestion],
        lesson_size: int,
    ) -> list[LessonQuestion]:
        if not review_questions:
            return base_questions[:lesson_size]

        result: list[LessonQuestion] = []
        review_queue = list(review_questions)
        # Insert review prompts after a few questions to mimic spaced repetition.
        insertion_points = {2, 4}

        for index, question in enumerate(base_questions, start=1):
            result.append(question)
            if review_queue and index in insertion_points and len(result) < lesson_size:
                result.append(review_queue.pop(0))

        while review_queue and len(result) < lesson_size:
            result.append(review_queue.pop(0))

        return result[:lesson_size]


smart_learning_service = SmartLearningService()
