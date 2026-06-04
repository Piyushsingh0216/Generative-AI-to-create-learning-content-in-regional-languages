from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.ai_usage import AIUsage
from app.models.language_progress import LanguageProgress
from app.models.user import User
from app.models.weak_word import WeakWord
from app.schemas.lesson import (
    LessonCompletionRequest,
    LessonCompletionResponse,
    LessonDifficulty,
    LessonQuestion,
    LessonResponse,
)
from app.services.gamification_service import (
    calculate_level,
    calculate_level_progress_percent,
    calculate_lesson_xp,
    evaluate_rewards,
    reward_labels,
    update_streak,
)
from app.services.smart_learning_service import LESSON_SIZE, DIFFICULTY_ORDER, smart_learning_service


router = APIRouter(prefix="/api/lessons", tags=["Lessons"])


LESSON_BANK: dict[str, dict[str, object]] = {
    "hi": {
        "language_label": "Hindi",
        "lesson_title": "Hindi Smart Practice",
        "questions": [
            LessonQuestion(
                id="hi-easy-1",
                type="mcq",
                prompt="What does 'Namaste' mean?",
                options=["Hello", "Thank you", "Good night", "Sorry"],
                answer="Hello",
                difficulty="easy",
                focus_text="Namaste",
            ),
            LessonQuestion(
                id="hi-easy-2",
                type="fill_blank",
                prompt="Fill in the blank: 'Dhanyavaad' means ____.",
                answer="Thank you",
                difficulty="easy",
                focus_text="Dhanyavaad",
            ),
            LessonQuestion(
                id="hi-easy-3",
                type="match_words",
                prompt="Match this Hindi word: 'Pani'",
                options=["Water", "Food", "Book", "Sun"],
                answer="Water",
                difficulty="easy",
                focus_text="Pani",
            ),
            LessonQuestion(
                id="hi-medium-1",
                type="listening_text",
                prompt="What is the meaning of this spoken phrase?",
                listening_text="Aap kaise ho?",
                options=["How are you?", "Where are you?", "What is your name?", "Come here"],
                answer="How are you?",
                difficulty="medium",
                focus_text="Aap kaise ho?",
            ),
            LessonQuestion(
                id="hi-medium-2",
                type="mcq",
                prompt="Choose the correct Hindi phrase for 'I am fine'.",
                options=["Main theek hoon", "Mujhe pata nahi", "Aap kahan ho", "Kal milte hain"],
                answer="Main theek hoon",
                difficulty="medium",
                focus_text="Main theek hoon",
            ),
            LessonQuestion(
                id="hi-hard-1",
                type="mcq",
                prompt="Translate the sentence: 'Mujhe paani chahiye.'",
                options=["I need water.", "I like tea.", "I am thirsty.", "Bring water."],
                answer="I need water.",
                difficulty="hard",
                focus_text="Mujhe paani chahiye",
            ),
            LessonQuestion(
                id="hi-hard-2",
                type="mcq",
                prompt="Translate: 'Kya aap madad kar sakte hain?'",
                options=["Can you help?", "Where are you from?", "Do you need food?", "Can I go now?"],
                answer="Can you help?",
                difficulty="hard",
                focus_text="Kya aap madad kar sakte hain",
            ),
        ],
    },
    "bho": {
        "language_label": "Bhojpuri",
        "lesson_title": "Bhojpuri Smart Practice",
        "questions": [
            LessonQuestion(
                id="bho-easy-1",
                type="mcq",
                prompt="What does 'Pranam' mean in Bhojpuri?",
                options=["Greeting", "Market", "School", "Dinner"],
                answer="Greeting",
                difficulty="easy",
                focus_text="Pranam",
            ),
            LessonQuestion(
                id="bho-easy-2",
                type="fill_blank",
                prompt="Fill in the blank: 'Pani' means ____.",
                answer="Water",
                difficulty="easy",
                focus_text="Pani",
            ),
            LessonQuestion(
                id="bho-easy-3",
                type="match_words",
                prompt="Match this Bhojpuri word: 'Roti'",
                options=["Bread", "Salt", "Milk", "Rice"],
                answer="Bread",
                difficulty="easy",
                focus_text="Roti",
            ),
            LessonQuestion(
                id="bho-medium-1",
                type="listening_text",
                prompt="What is the meaning of this spoken phrase?",
                listening_text="Ka haal ba?",
                options=["How are you?", "Who are you?", "What time is it?", "Please sit"],
                answer="How are you?",
                difficulty="medium",
                focus_text="Ka haal ba?",
            ),
            LessonQuestion(
                id="bho-medium-2",
                type="mcq",
                prompt="Choose the Bhojpuri phrase for 'I am fine'.",
                options=["Hum thik bani", "Tu kaha jaat ba", "Ka naam ba", "Pani lao"],
                answer="Hum thik bani",
                difficulty="medium",
                focus_text="Hum thik bani",
            ),
            LessonQuestion(
                id="bho-hard-1",
                type="mcq",
                prompt="Translate: 'Hamra ke pani chahi.'",
                options=["I need water.", "I need food.", "I need help.", "I need rest."],
                answer="I need water.",
                difficulty="hard",
                focus_text="Hamra ke pani chahi",
            ),
            LessonQuestion(
                id="bho-hard-2",
                type="mcq",
                prompt="Translate: 'Rasta bata di.'",
                options=["Please show the way.", "Please sit here.", "Bring some water.", "Come tomorrow."],
                answer="Please show the way.",
                difficulty="hard",
                focus_text="Rasta bata di",
            ),
        ],
    },
    "ta": {
        "language_label": "Tamil",
        "lesson_title": "Tamil Smart Practice",
        "questions": [
            LessonQuestion(
                id="ta-easy-1",
                type="mcq",
                prompt="What does 'Vanakkam' mean?",
                options=["Hello", "Goodbye", "Morning", "Friend"],
                answer="Hello",
                difficulty="easy",
                focus_text="Vanakkam",
            ),
            LessonQuestion(
                id="ta-easy-2",
                type="fill_blank",
                prompt="Fill in the blank: 'Nandri' means ____.",
                answer="Thank you",
                difficulty="easy",
                focus_text="Nandri",
            ),
            LessonQuestion(
                id="ta-easy-3",
                type="match_words",
                prompt="Match this Tamil word: 'Thanni'",
                options=["Water", "Road", "Tree", "Window"],
                answer="Water",
                difficulty="easy",
                focus_text="Thanni",
            ),
            LessonQuestion(
                id="ta-medium-1",
                type="listening_text",
                prompt="What is the meaning of this spoken phrase?",
                listening_text="Neenga eppadi irukeenga?",
                options=["How are you?", "Where do you live?", "What did you eat?", "Come tomorrow"],
                answer="How are you?",
                difficulty="medium",
                focus_text="Neenga eppadi irukeenga",
            ),
            LessonQuestion(
                id="ta-medium-2",
                type="mcq",
                prompt="Choose the Tamil phrase for 'I am fine'.",
                options=["Naan nalla irukken", "Neenga enga pogireenga", "Sapadu venuma", "Naalai varen"],
                answer="Naan nalla irukken",
                difficulty="medium",
                focus_text="Naan nalla irukken",
            ),
            LessonQuestion(
                id="ta-hard-1",
                type="mcq",
                prompt="Translate: 'Enakku thanni venum.'",
                options=["I need water.", "I need rice.", "I need help.", "I need sleep."],
                answer="I need water.",
                difficulty="hard",
                focus_text="Enakku thanni venum",
            ),
            LessonQuestion(
                id="ta-hard-2",
                type="mcq",
                prompt="Translate: 'Ungal udhavi venum.'",
                options=["I need your help.", "I need your book.", "I need your phone.", "I need your bag."],
                answer="I need your help.",
                difficulty="hard",
                focus_text="Ungal udhavi venum",
            ),
        ],
    },
    "bn": {
        "language_label": "Bengali",
        "lesson_title": "Bengali Smart Practice",
        "questions": [
            LessonQuestion(
                id="bn-easy-1",
                type="mcq",
                prompt="What does 'Nomoskar' mean?",
                options=["Hello", "Thank you", "Goodbye", "Please"],
                answer="Hello",
                difficulty="easy",
                focus_text="Nomoskar",
            ),
            LessonQuestion(
                id="bn-easy-2",
                type="fill_blank",
                prompt="Fill in the blank: 'Dhonnobad' means ____.",
                answer="Thank you",
                difficulty="easy",
                focus_text="Dhonnobad",
            ),
            LessonQuestion(
                id="bn-easy-3",
                type="match_words",
                prompt="Match this Bengali word: 'Jol'",
                options=["Water", "Fire", "Fruit", "River"],
                answer="Water",
                difficulty="easy",
                focus_text="Jol",
            ),
            LessonQuestion(
                id="bn-medium-1",
                type="listening_text",
                prompt="What is the meaning of this spoken phrase?",
                listening_text="Tumi kemon acho?",
                options=["How are you?", "What is your name?", "Where are you going?", "Open the door"],
                answer="How are you?",
                difficulty="medium",
                focus_text="Tumi kemon acho",
            ),
            LessonQuestion(
                id="bn-medium-2",
                type="mcq",
                prompt="Choose the Bengali phrase for 'I am fine'.",
                options=["Ami bhalo achi", "Ami bari jabo", "Tumi kothay", "Ami khide peyechi"],
                answer="Ami bhalo achi",
                difficulty="medium",
                focus_text="Ami bhalo achi",
            ),
            LessonQuestion(
                id="bn-hard-1",
                type="mcq",
                prompt="Translate: 'Amar jol dorkar.'",
                options=["I need water.", "I need food.", "I need a pen.", "I need tea."],
                answer="I need water.",
                difficulty="hard",
                focus_text="Amar jol dorkar",
            ),
            LessonQuestion(
                id="bn-hard-2",
                type="mcq",
                prompt="Translate: 'Tumi ki amake shahajjo korte parbe?'",
                options=["Can you help me?", "Can you call me?", "Can you hear me?", "Can you wait for me?"],
                answer="Can you help me?",
                difficulty="hard",
                focus_text="Tumi ki amake shahajjo korte parbe",
            ),
        ],
    },
}


def _normalize_answer(value: str | None) -> str:
    return (value or "").strip().casefold()


def _extract_recent_accuracies(rows: list[AIUsage], language_code: str, limit: int = 3) -> list[float]:
    accuracies: list[float] = []
    for row in rows:
        metadata = row.metadata_json or {}
        if metadata.get("language_code") != language_code:
            continue
        accuracy = metadata.get("accuracy")
        if isinstance(accuracy, (int, float)):
            accuracies.append(float(accuracy))
            if len(accuracies) >= limit:
                break
    return accuracies


def _dominant_difficulty(questions: list[LessonQuestion]) -> LessonDifficulty:
    if not questions:
        return "easy"
    counts = Counter(item.difficulty for item in questions)
    return sorted(
        counts.items(),
        key=lambda item: (item[1], DIFFICULTY_ORDER.index(item[0])),
        reverse=True,
    )[0][0]


@router.get("/{language_code}", response_model=LessonResponse)
def get_lesson(
    language_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    language_code = language_code.lower().strip()
    language_bank = LESSON_BANK.get(language_code)
    if not language_bank:
        raise HTTPException(status_code=404, detail="Lesson not found for this language.")

    question_bank: list[LessonQuestion] = language_bank["questions"]
    progress = (
        db.query(LanguageProgress)
        .filter(
            LanguageProgress.user_id == current_user.id,
            LanguageProgress.language_code == language_code,
        )
        .first()
    )
    weak_words = (
        db.query(WeakWord)
        .filter(
            WeakWord.user_id == current_user.id,
            WeakWord.language_code == language_code,
            WeakWord.incorrect_count > 0,
        )
        .all()
    )
    recent_rows = (
        db.query(AIUsage)
        .filter(
            AIUsage.user_id == current_user.id,
            AIUsage.action == "lesson_complete",
        )
        .order_by(AIUsage.created_at.desc())
        .limit(30)
        .all()
    )
    recent_accuracies = _extract_recent_accuracies(recent_rows, language_code=language_code)

    target_difficulty = smart_learning_service.determine_difficulty(
        level=progress.level if progress else 1,
        weak_words=weak_words,
        recent_accuracies=recent_accuracies,
    )
    selected_questions = smart_learning_service.select_personalized_questions(
        question_bank=question_bank,
        target_difficulty=target_difficulty,
        weak_words=weak_words,
        lesson_size=LESSON_SIZE,
    )
    review_count = sum(1 for item in selected_questions if item.is_review)

    return LessonResponse(
        language_code=language_code,
        language_label=language_bank["language_label"],
        lesson_title=f"{language_bank['lesson_title']} ({target_difficulty.title()})",
        difficulty=target_difficulty,
        review_question_count=review_count,
        questions=selected_questions,
    )


@router.post("/complete", response_model=LessonCompletionResponse)
def complete_lesson(
    payload: LessonCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    language_code = payload.language_code.lower().strip()
    language_bank = LESSON_BANK.get(language_code)
    if not language_bank:
        raise HTTPException(status_code=404, detail="Lesson not found for this language.")

    if not payload.answers:
        raise HTTPException(status_code=400, detail="Please answer all lesson questions before submitting.")

    seen_ids: set[str] = set()
    answer_map: dict[str, str] = {}
    question_bank: list[LessonQuestion] = language_bank["questions"]
    question_by_id = {question.id: question for question in question_bank}

    for item in payload.answers:
        if item.question_id in seen_ids:
            raise HTTPException(status_code=400, detail="Duplicate question submissions are not allowed.")
        seen_ids.add(item.question_id)

        question = question_by_id.get(item.question_id)
        if not question:
            raise HTTPException(status_code=400, detail=f"Unknown question id: {item.question_id}")
        if not _normalize_answer(item.answer):
            raise HTTPException(status_code=400, detail="Please answer all lesson questions before submitting.")
        answer_map[item.question_id] = item.answer

    correct_answers, evaluated_answers = smart_learning_service.evaluate_submissions(question_by_id, answer_map)
    total_questions = len(answer_map)
    earned_xp, base_xp, bonus_xp = calculate_lesson_xp(correct_answers, total_questions)

    progress = (
        db.query(LanguageProgress)
        .filter(
            LanguageProgress.user_id == current_user.id,
            LanguageProgress.language_code == language_code,
        )
        .first()
    )
    if not progress:
        progress = LanguageProgress(
            user_id=current_user.id,
            language_code=language_code,
            xp=0,
            streak=0,
            level=1,
            lessons_completed=0,
            rewards=[],
        )
        db.add(progress)
        db.flush()

    attempted_at = datetime.now(timezone.utc)
    incorrect_focus_words = smart_learning_service.track_weak_words(
        db=db,
        user_id=current_user.id,
        language_code=language_code,
        evaluated_answers=evaluated_answers,
        attempted_at=attempted_at,
    )

    today = attempted_at.date()
    progress.streak = update_streak(progress.streak, progress.last_activity_date, today)
    progress.last_activity_date = today
    progress.lessons_completed += 1
    progress.xp += earned_xp
    progress.level = calculate_level(progress.xp)
    updated_rewards, new_rewards = evaluate_rewards(
        current_reward_ids=progress.rewards,
        lessons_completed=progress.lessons_completed,
        streak=progress.streak,
        xp=progress.xp,
    )
    progress.rewards = updated_rewards

    submitted_questions = [question_by_id[item.question_id] for item in payload.answers]
    effective_difficulty = _dominant_difficulty(submitted_questions)
    accuracy = (correct_answers / total_questions) if total_questions else 0.0
    db.add(
        AIUsage(
            user_id=current_user.id,
            action="lesson_complete",
            metadata_json={
                "language_code": language_code,
                "difficulty": effective_difficulty,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "accuracy": accuracy,
                "incorrect_focus_words": incorrect_focus_words,
            },
        )
    )

    db.commit()
    db.refresh(progress)

    return LessonCompletionResponse(
        language_code=language_code,
        language_label=language_bank["language_label"],
        difficulty=effective_difficulty,
        correct_answers=correct_answers,
        total_questions=total_questions,
        base_xp=base_xp,
        bonus_xp=bonus_xp,
        earned_xp=earned_xp,
        total_xp=progress.xp,
        streak=progress.streak,
        level=progress.level,
        level_progress_percent=calculate_level_progress_percent(progress.xp),
        rewards=reward_labels(progress.rewards),
        newly_unlocked_rewards=reward_labels(new_rewards),
        incorrect_focus_words=incorrect_focus_words,
    )
