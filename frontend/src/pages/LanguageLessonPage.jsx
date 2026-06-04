import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import NavigateNextRoundedIcon from "@mui/icons-material/NavigateNextRounded";

import { useNavigate, useParams } from "react-router-dom";

import CharacterAssistant from "../components/CharacterAssistant";
import LessonQuestionCard from "../components/LessonQuestionCard";
import RewardBadgeList from "../components/RewardBadgeList";
import DashboardLayout from "../layouts/DashboardLayout";
import api from "../services/api";

const normalizeAnswer = (value) => value.trim().toLowerCase();

function LanguageLessonPage() {
  const navigate = useNavigate();
  const { languageCode = "" } = useParams();

  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState([]);
  const [completionData, setCompletionData] = useState(null);
  const [submittingCompletion, setSubmittingCompletion] = useState(false);
  const [assistantFeedback, setAssistantFeedback] = useState({
    token: 0,
    result: null,
    message: "",
  });

  useEffect(() => {
    const loadLesson = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await api.get(`/lessons/${languageCode}`);
        setLesson(response.data);
        setCurrentQuestionIndex(0);
        setAnswers({});
        setResults([]);
        setCompletionData(null);
        setAssistantFeedback({ token: 0, result: null, message: "" });
      } catch (err) {
        setError(err?.response?.data?.detail || "Failed to load lesson.");
        setLesson(null);
      } finally {
        setLoading(false);
      }
    };

    loadLesson();
  }, [languageCode]);

  const totalQuestions = lesson?.questions?.length || 0;
  const isCompleted = !!lesson && currentQuestionIndex >= totalQuestions;
  const currentQuestion = !isCompleted ? lesson?.questions?.[currentQuestionIndex] : null;

  const progressValue = useMemo(() => {
    if (!totalQuestions) return 0;
    if (isCompleted) return 100;
    return (Math.min(currentQuestionIndex + 1, totalQuestions) / totalQuestions) * 100;
  }, [currentQuestionIndex, isCompleted, totalQuestions]);

  const score = useMemo(() => results.filter((item) => item.isCorrect).length, [results]);

  const handleAnswerChange = (value) => {
    if (!currentQuestion) return;
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }));
    if (error) setError("");
  };

  const handleNext = async () => {
    if (!currentQuestion) return;

    const answerValue = answers[currentQuestion.id];
    const userAnswer = typeof answerValue === "string" ? answerValue.trim() : "";

    if (!userAnswer) {
      setError("Please answer the current question before moving to the next one.");
      return;
    }

    const isCorrect = normalizeAnswer(userAnswer) === normalizeAnswer(currentQuestion.answer);
    const feedbackMessage = isCorrect
      ? "Great answer. Keep it up."
      : "Not quite. We will practice this again.";

    setAssistantFeedback((prev) => ({
      token: prev.token + 1,
      result: isCorrect ? "correct" : "wrong",
      message: feedbackMessage,
    }));

    const nextResults = [
      ...results,
      {
        question_id: currentQuestion.id,
        selected_answer: userAnswer,
        isCorrect,
      },
    ];
    const nextAnswers = { ...answers, [currentQuestion.id]: userAnswer };
    const isLastQuestion = currentQuestionIndex + 1 === totalQuestions;

    setAnswers(nextAnswers);
    setError("");

    if (!isLastQuestion) {
      setResults(nextResults);
      setCurrentQuestionIndex((prev) => prev + 1);
      return;
    }

    setSubmittingCompletion(true);
    try {
      const payload = {
        language_code: lesson.language_code,
        answers: lesson.questions.map((question) => ({
          question_id: question.id,
          answer: nextAnswers[question.id] || "",
        })),
      };
      const response = await api.post("/lessons/complete", payload);
      setResults(nextResults);
      setCompletionData(response.data);
      setCurrentQuestionIndex((prev) => prev + 1);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to complete lesson.");
    } finally {
      setSubmittingCompletion(false);
    }
  };

  return (
    <DashboardLayout>
      <Stack spacing={2.5}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent="space-between"
          alignItems={{ sm: "center" }}
          spacing={1}
        >
          <Typography variant="h5">
            {lesson ? `${lesson.language_label} Learning` : "Language Learning"}
          </Typography>
          <Button
            variant="text"
            startIcon={<ArrowBackRoundedIcon />}
            onClick={() => navigate("/dashboard")}
          >
            Back to Dashboard
          </Button>
        </Stack>

        {error ? <Alert severity="error">{error}</Alert> : null}

        {loading ? (
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Loading lesson...
              </Typography>
            </CardContent>
          </Card>
        ) : null}

        {!loading && lesson && !isCompleted ? (
          <>
            <Card>
              <CardContent>
                <Stack spacing={1.4}>
                  <Typography variant="subtitle1">{lesson.lesson_title}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Difficulty: {(lesson.difficulty || "easy").toUpperCase()}
                  </Typography>
                  {lesson.review_question_count ? (
                    <Typography variant="body2" color="text.secondary">
                      Review questions included: {lesson.review_question_count}
                    </Typography>
                  ) : null}
                  <Typography variant="body2" color="text.secondary">
                    Question {currentQuestionIndex + 1}/{totalQuestions}
                  </Typography>
                  <LinearProgress variant="determinate" value={progressValue} />
                </Stack>
              </CardContent>
            </Card>

            <LessonQuestionCard
              question={currentQuestion}
              answerValue={answers[currentQuestion.id] || ""}
              onAnswerChange={handleAnswerChange}
            />

            <Box>
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={submittingCompletion}
                endIcon={<NavigateNextRoundedIcon />}
              >
                {submittingCompletion
                  ? "Submitting..."
                  : currentQuestionIndex + 1 === totalQuestions
                    ? "Finish Lesson"
                    : "Next"}
              </Button>
            </Box>
          </>
        ) : null}

        {!loading && lesson && isCompleted ? (
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Typography variant="h6">
                  {"Lesson Completed "}
                  {"\u{1F389}"}
                </Typography>
                <Typography variant="body1">
                  Score: {completionData?.correct_answers ?? score}/
                  {completionData?.total_questions ?? totalQuestions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You answered {completionData?.correct_answers ?? score} question
                  {(completionData?.correct_answers ?? score) === 1 ? "" : "s"} correctly.
                </Typography>
                {completionData ? (
                  <>
                    <Typography variant="body2" color="text.secondary">
                      XP earned: +{completionData.earned_xp} ({completionData.base_xp} base +{" "}
                      {completionData.bonus_xp} bonus)
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total XP: {completionData.total_xp} | Level: {completionData.level} | Streak:{" "}
                      {completionData.streak} days
                    </Typography>
                    <Stack spacing={0.6}>
                      <Typography variant="body2" color="text.secondary">
                        Rewards
                      </Typography>
                      <RewardBadgeList rewards={completionData.rewards} />
                    </Stack>
                    {completionData.newly_unlocked_rewards?.length ? (
                      <Alert severity="success">
                        New reward unlocked: {completionData.newly_unlocked_rewards.join(", ")}
                      </Alert>
                    ) : null}
                    {completionData.incorrect_focus_words?.length ? (
                      <Alert severity="info">
                        Let&apos;s practice this again next time:{" "}
                        {completionData.incorrect_focus_words.join(", ")}
                      </Alert>
                    ) : null}
                  </>
                ) : null}
                <Box>
                  <Button variant="contained" onClick={() => navigate("/dashboard")}>
                    Back to Dashboard
                  </Button>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        ) : null}

        {!loading && !lesson && !error ? (
          <Alert severity="info">No lesson is available for this language yet.</Alert>
        ) : null}

        {!loading && lesson ? (
          <CharacterAssistant
            languageCode={lesson.language_code}
            currentQuestion={currentQuestion}
            feedbackEvent={assistantFeedback}
            isLessonCompleted={isCompleted}
          />
        ) : null}
      </Stack>
    </DashboardLayout>
  );
}

export default LanguageLessonPage;
