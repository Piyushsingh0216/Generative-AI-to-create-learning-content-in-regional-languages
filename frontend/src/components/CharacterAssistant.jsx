import { keyframes } from "@emotion/react";
import ReplayRoundedIcon from "@mui/icons-material/ReplayRounded";
import VolumeOffRoundedIcon from "@mui/icons-material/VolumeOffRounded";
import VolumeUpRoundedIcon from "@mui/icons-material/VolumeUpRounded";
import {
  Box,
  Button,
  Card,
  CardContent,
  IconButton,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import CHARACTER_PROFILES from "../data/characterProfiles";

const idleFloat = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
`;

const talkingPulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.04); }
`;

const happyBounce = keyframes`
  0%, 100% { transform: translateY(0); }
  30% { transform: translateY(-7px); }
  60% { transform: translateY(-3px); }
`;

const sadShake = keyframes`
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
`;

const moodAnimation = {
  idle: `${idleFloat} 2.6s ease-in-out infinite`,
  talking: `${talkingPulse} 1.1s ease-in-out infinite`,
  happy: `${happyBounce} 0.9s ease-in-out infinite`,
  sad: `${sadShake} 0.6s ease-in-out infinite`,
};

const clearTimer = (timerRef) => {
  if (timerRef.current) {
    clearTimeout(timerRef.current);
    timerRef.current = null;
  }
};

function CharacterAssistant({
  languageCode,
  currentQuestion,
  feedbackEvent,
  isLessonCompleted,
}) {
  const profile = CHARACTER_PROFILES[languageCode] || CHARACTER_PROFILES.default;

  const [mood, setMood] = useState("idle");
  const [assistantText, setAssistantText] = useState(
    "I can read each question aloud for you."
  );
  const [muted, setMuted] = useState(false);
  const [speechRate, setSpeechRate] = useState(1);
  const [voices, setVoices] = useState([]);

  const moodResetTimerRef = useRef(null);

  useEffect(() => {
    if (!("speechSynthesis" in window)) return undefined;
    const synth = window.speechSynthesis;
    const syncVoices = () => setVoices(synth.getVoices());

    syncVoices();
    if (typeof synth.addEventListener === "function") {
      synth.addEventListener("voiceschanged", syncVoices);
      return () => {
        synth.removeEventListener("voiceschanged", syncVoices);
        synth.cancel();
      };
    }

    synth.onvoiceschanged = syncVoices;
    return () => {
      synth.onvoiceschanged = null;
      synth.cancel();
    };
  }, []);

  useEffect(() => () => clearTimer(moodResetTimerRef), []);

  const preferredVoice = useMemo(() => {
    if (!voices.length) return null;
    const fullMatch = voices.find(
      (voice) => voice.lang?.toLowerCase() === profile.voiceLang.toLowerCase()
    );
    if (fullMatch) return fullMatch;

    const primaryCode = profile.voiceLang.split("-")[0].toLowerCase();
    return (
      voices.find((voice) => voice.lang?.toLowerCase().startsWith(primaryCode)) || null
    );
  }, [profile.voiceLang, voices]);

  const speak = useCallback(
    (text, onEnd) => {
      if (!text) {
        if (onEnd) onEnd();
        return;
      }
      if (!("speechSynthesis" in window) || muted) {
        if (onEnd) onEnd();
        return;
      }

      const synth = window.speechSynthesis;
      synth.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = profile.voiceLang;
      utterance.rate = speechRate;
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      utterance.onend = () => {
        if (onEnd) onEnd();
      };
      utterance.onerror = () => {
        if (onEnd) onEnd();
      };
      synth.speak(utterance);
    },
    [muted, preferredVoice, profile.voiceLang, speechRate]
  );

  const questionSpeechText = useMemo(() => {
    if (!currentQuestion) return "";
    if (currentQuestion.listening_text) {
      return `${currentQuestion.listening_text}. ${currentQuestion.prompt}`;
    }
    return currentQuestion.prompt;
  }, [currentQuestion]);

  useEffect(() => {
    if (!currentQuestion) return;

    clearTimer(moodResetTimerRef);
    setMood("talking");
    setAssistantText(
      currentQuestion.is_review
        ? "Let's practice this once more."
        : "New question ready."
    );

    speak(questionSpeechText, () => {
      setMood((prev) => (prev === "talking" ? "idle" : prev));
    });
  }, [currentQuestion?.id, currentQuestion?.is_review, questionSpeechText, speak]);

  useEffect(() => {
    if (!feedbackEvent?.token) return;
    clearTimer(moodResetTimerRef);

    if (feedbackEvent.result === "correct") {
      const line = feedbackEvent.message || "Great job. That is correct.";
      setMood("happy");
      setAssistantText(line);
      speak(line);
      moodResetTimerRef.current = setTimeout(() => setMood("idle"), 1200);
      return;
    }

    if (feedbackEvent.result === "wrong") {
      const line = feedbackEvent.message || "Almost there. We will practice this again.";
      setMood("sad");
      setAssistantText(line);
      speak(line);
      moodResetTimerRef.current = setTimeout(() => setMood("idle"), 1400);
    }
  }, [feedbackEvent?.message, feedbackEvent?.result, feedbackEvent?.token, speak]);

  useEffect(() => {
    if (!isLessonCompleted) return;
    clearTimer(moodResetTimerRef);
    const line = "Nice work. You completed this lesson.";
    setMood("happy");
    setAssistantText(line);
    speak(line);
  }, [isLessonCompleted, speak]);

  const handleReplay = () => {
    if (!questionSpeechText) return;
    clearTimer(moodResetTimerRef);
    setMood("talking");
    speak(questionSpeechText, () => setMood("idle"));
  };

  return (
    <Box
      sx={{
        position: { xs: "static", md: "fixed" },
        right: { md: 26 },
        bottom: { md: 22 },
        width: { xs: "100%", sm: 320, md: 280 },
        zIndex: 1000,
      }}
    >
      <Card>
        <CardContent>
          <Stack spacing={1.2}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Stack direction="row" spacing={1.2} alignItems="center">
                <Box
                  component="img"
                  src={profile.image}
                  alt={`${profile.name} assistant`}
                  sx={{
                    width: 58,
                    height: 58,
                    borderRadius: "50%",
                    border: "2px solid",
                    borderColor: "primary.main",
                    bgcolor: "#fff",
                    animation: moodAnimation[mood] || moodAnimation.idle,
                  }}
                />
                <Stack spacing={0}>
                  <Typography variant="subtitle2">{profile.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {profile.outfitLabel}
                  </Typography>
                </Stack>
              </Stack>
              <IconButton size="small" onClick={() => setMuted((prev) => !prev)}>
                {muted ? <VolumeOffRoundedIcon fontSize="small" /> : <VolumeUpRoundedIcon fontSize="small" />}
              </IconButton>
            </Stack>

            <Typography variant="body2" color="text.secondary">
              {assistantText}
            </Typography>

            <Stack direction="row" spacing={1} alignItems="center">
              <Button
                size="small"
                variant="outlined"
                startIcon={<ReplayRoundedIcon />}
                onClick={handleReplay}
                disabled={!questionSpeechText}
              >
                Hear again
              </Button>
              <Select
                size="small"
                value={speechRate}
                onChange={(event) => setSpeechRate(Number(event.target.value))}
                sx={{ minWidth: 92 }}
              >
                <MenuItem value={0.9}>0.9x</MenuItem>
                <MenuItem value={1}>1.0x</MenuItem>
                <MenuItem value={1.1}>1.1x</MenuItem>
              </Select>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}

export default CharacterAssistant;
