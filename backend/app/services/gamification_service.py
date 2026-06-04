from datetime import date
from typing import Iterable


FIRST_LESSON_REWARD = "first_lesson_completed"
THREE_DAY_STREAK_REWARD = "three_day_streak"
XP_100_REWARD = "xp_100_milestone"

REWARD_LABELS = {
    FIRST_LESSON_REWARD: "First Lesson Completed",
    THREE_DAY_STREAK_REWARD: "3-Day Streak",
    XP_100_REWARD: "100 XP Milestone",
}


def calculate_lesson_xp(correct_answers: int, total_questions: int) -> tuple[int, int, int]:
    base_xp = max(0, correct_answers) * 10
    bonus_xp = 20 if total_questions > 0 and correct_answers == total_questions else 0
    return base_xp + bonus_xp, base_xp, bonus_xp


def calculate_level(xp: int) -> int:
    if xp <= 100:
        return 1
    if xp <= 300:
        return 2
    return 3


def calculate_level_progress_percent(xp: int) -> int:
    level = calculate_level(xp)
    if level == 1:
        start, end = 0, 100
    elif level == 2:
        start, end = 101, 300
    else:
        start, end = 301, 600

    bounded_xp = min(max(xp, start), end)
    span = end - start
    if span <= 0:
        return 100
    return int(round(((bounded_xp - start) / span) * 100))


def update_streak(current_streak: int, last_activity: date | None, today: date) -> int:
    if last_activity is None:
        return 1

    delta_days = (today - last_activity).days
    if delta_days <= 0:
        return max(current_streak, 1)
    if delta_days == 1:
        return max(current_streak, 0) + 1
    return 1


def evaluate_rewards(
    current_reward_ids: Iterable[str] | None,
    lessons_completed: int,
    streak: int,
    xp: int,
) -> tuple[list[str], list[str]]:
    reward_ids = list(dict.fromkeys(current_reward_ids or []))
    known = set(reward_ids)
    newly_unlocked: list[str] = []

    candidates = [
        (FIRST_LESSON_REWARD, lessons_completed >= 1),
        (THREE_DAY_STREAK_REWARD, streak >= 3),
        (XP_100_REWARD, xp >= 100),
    ]

    for reward_id, unlocked in candidates:
        if unlocked and reward_id not in known:
            reward_ids.append(reward_id)
            known.add(reward_id)
            newly_unlocked.append(reward_id)

    return reward_ids, newly_unlocked


def reward_labels(reward_ids: Iterable[str] | None) -> list[str]:
    return [REWARD_LABELS.get(item, item) for item in (reward_ids or [])]
