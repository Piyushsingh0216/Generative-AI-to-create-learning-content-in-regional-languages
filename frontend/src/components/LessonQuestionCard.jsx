import { Alert, Button, Card, CardContent, Paper, Stack, TextField, Typography } from "@mui/material";

import {
  CHOICE_BASED_QUESTION_TYPES,
  LESSON_QUESTION_TYPE_LABELS,
} from "../data/lessonQuestionTypes";

function LessonQuestionCard({ question, answerValue, onAnswerChange }) {
  const isChoiceBased = CHOICE_BASED_QUESTION_TYPES.includes(question.type);

  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          {question.is_review ? (
            <Alert severity="info">Let&apos;s practice this again.</Alert>
          ) : null}

          <Typography variant="subtitle2" color="text.secondary">
            {LESSON_QUESTION_TYPE_LABELS[question.type] || "Question"}
          </Typography>

          {question.type === "listening_text" && question.listening_text ? (
            <Paper variant="outlined" sx={{ p: 1.5 }}>
              <Typography variant="body2" color="text.secondary">
                Listening prompt (text-based)
              </Typography>
              <Typography variant="body1" sx={{ mt: 0.8 }}>
                {question.listening_text}
              </Typography>
            </Paper>
          ) : null}

          <Typography variant="h6">{question.prompt}</Typography>

          {isChoiceBased ? (
            <Stack spacing={1}>
              {(question.options || []).map((option) => (
                <Button
                  key={option}
                  variant={answerValue === option ? "contained" : "outlined"}
                  onClick={() => onAnswerChange(option)}
                  sx={{ justifyContent: "flex-start" }}
                >
                  {option}
                </Button>
              ))}
            </Stack>
          ) : (
            <TextField
              fullWidth
              label="Type your answer"
              placeholder="Enter your answer"
              value={answerValue}
              onChange={(e) => onAnswerChange(e.target.value)}
            />
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

export default LessonQuestionCard;
