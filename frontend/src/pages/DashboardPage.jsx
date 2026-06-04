import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import UploadFileRoundedIcon from "@mui/icons-material/UploadFileRounded";
import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import QuizRoundedIcon from "@mui/icons-material/QuizRounded";
import TranslateRoundedIcon from "@mui/icons-material/TranslateRounded";
import { useNavigate } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import LanguageLearningCard from "../components/LanguageLearningCard";
import StatCard from "../components/StatCard";
import api from "../services/api";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
  { code: "mr", label: "Marathi" },
  { code: "bn", label: "Bengali" },
  { code: "gu", label: "Gujarati" },
  { code: "kn", label: "Kannada" },
];

const LEARN_NEW_LANGUAGE_CARDS = [
  { code: "hi", language: "Hindi" },
  { code: "bho", language: "Bhojpuri" },
  { code: "ta", language: "Tamil" },
  { code: "bn", language: "Bengali" },
];

const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || "http://localhost:8000";

function DashboardPage() {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedUploadId, setSelectedUploadId] = useState("");

  const [file, setFile] = useState(null);
  const [topic, setTopic] = useState("");
  const [language, setLanguage] = useState("en");
  const [enableVoice, setEnableVoice] = useState(false);

  const [manualText, setManualText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [summary, setSummary] = useState(null);
  const [questions, setQuestions] = useState(null);
  const [audioUrl, setAudioUrl] = useState("");

  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([]);

  const [loading, setLoading] = useState({
    upload: false,
    translate: false,
    summary: false,
    questions: false,
    chat: false,
  });
  const [error, setError] = useState("");

  const selectedUpload = useMemo(() => {
    if (!selectedUploadId) return null;
    const normalizedId = Number(selectedUploadId);
    return history.find((item) => item.id === normalizedId) || null;
  }, [history, selectedUploadId]);

  const languageProgressByCode = useMemo(() => {
    const progress = analytics?.language_progress || [];
    return progress.reduce((acc, item) => {
      acc[item.language_code] = item;
      return acc;
    }, {});
  }, [analytics]);

  const learnLanguageCards = useMemo(
    () =>
      LEARN_NEW_LANGUAGE_CARDS.map((item) => {
        const progress = languageProgressByCode[item.code];
        return {
          ...item,
          progress: progress?.level_progress_percent ?? 0,
          xp: progress?.xp ?? 0,
          streak: progress?.streak ?? 0,
          level: progress?.level ?? 1,
          rewards: progress?.rewards ?? [],
        };
      }),
    [languageProgressByCode]
  );

  const fetchData = async () => {
    try {
      const [overviewResponse, historyResponse] = await Promise.all([
        api.get("/dashboard/overview"),
        api.get("/uploads/history"),
      ]);
      setAnalytics(overviewResponse.data);
      setHistory(historyResponse.data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load dashboard data.");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      api.post("/dashboard/time-spent", { seconds: 60 }).catch(() => {});
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const setActionLoading = (key, value) => {
    setLoading((prev) => ({ ...prev, [key]: value }));
  };

  const resolveContextPayload = () => {
    if (selectedUploadId) {
      return { upload_id: Number(selectedUploadId) };
    }
    if (manualText.trim()) {
      return { text: manualText.trim() };
    }
    return null;
  };

  const normalizeMediaUrl = (path) => {
    if (!path) return "";
    if (path.startsWith("http://") || path.startsWith("https://")) return path;
    return `${backendOrigin}${path}`;
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Choose a file before uploading.");
      return;
    }
    setError("");
    setActionLoading("upload", true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (topic.trim()) formData.append("topic", topic.trim());

      const response = await api.post("/uploads/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSelectedUploadId(response.data.id);
      setManualText(response.data.extracted_text_preview || "");
      setFile(null);
      setTopic("");
      await fetchData();
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed.");
    } finally {
      setActionLoading("upload", false);
    }
  };

  const handleTranslate = async () => {
    if (!manualText.trim()) {
      setError("Add text for translation.");
      return;
    }
    setError("");
    setActionLoading("translate", true);
    try {
      const response = await api.post("/ai/translate", {
        text: manualText,
        target_lang: language,
        enable_voice: enableVoice,
      });
      setTranslatedText(response.data.translated_text);
      setAudioUrl(normalizeMediaUrl(response.data.audio_url));
    } catch (err) {
      setError(err?.response?.data?.detail || "Translation failed.");
    } finally {
      setActionLoading("translate", false);
    }
  };

  const handleSummary = async () => {
    const payload = resolveContextPayload();
    if (!payload) {
      setError("Select an upload or enter manual text for summary.");
      return;
    }
    setError("");
    setActionLoading("summary", true);
    try {
      const response = await api.post("/ai/summarize", {
        ...payload,
        target_lang: language,
        enable_voice: enableVoice,
      });
      setSummary(response.data);
      setAudioUrl(normalizeMediaUrl(response.data.audio_url));
      await fetchData();
    } catch (err) {
      setError(err?.response?.data?.detail || "Summary generation failed.");
    } finally {
      setActionLoading("summary", false);
    }
  };

  const handleQuestions = async () => {
    const payload = resolveContextPayload();
    if (!payload) {
      setError("Select an upload or enter manual text for question generation.");
      return;
    }
    setError("");
    setActionLoading("questions", true);
    try {
      const response = await api.post("/ai/questions", payload);
      setQuestions(response.data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Question generation failed.");
    } finally {
      setActionLoading("questions", false);
    }
  };

  const handleChatSend = async () => {
    if (!chatInput.trim()) return;
    const payload = resolveContextPayload();
    if (!payload) {
      setError("Select an upload or enter manual text before using chatbot.");
      return;
    }

    const userMessage = { role: "user", content: chatInput.trim() };
    const nextHistory = [...chatMessages, userMessage];
    setChatMessages(nextHistory);
    setChatInput("");
    setError("");
    setActionLoading("chat", true);

    try {
      const response = await api.post("/ai/chat", {
        ...payload,
        message: userMessage.content,
        history: nextHistory.slice(-6),
      });
      setChatMessages((prev) => [...prev, { role: "assistant", content: response.data.answer }]);
    } catch (err) {
      setError(err?.response?.data?.detail || "Chatbot request failed.");
    } finally {
      setActionLoading("chat", false);
    }
  };

  const handleStartLanguageLesson = (item) => {
    navigate(`/dashboard/lesson/${item.code}`);
  };

  return (
    <DashboardLayout>
      <Stack spacing={2.5}>
        <Typography variant="h5">Learning Workspace</Typography>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard title="Uploads" value={analytics?.total_uploads ?? 0} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard title="Summaries" value={analytics?.total_summaries ?? 0} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Time Spent"
              value={`${Math.floor((analytics?.total_time_spent_seconds ?? 0) / 60)} min`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard title="Topics Learned" value={(analytics?.topics_learned ?? []).length} />
          </Grid>
        </Grid>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Upload Document</Typography>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<UploadFileRoundedIcon />}
                  >
                    {file ? file.name : "Choose file (.pdf/.docx/.pptx/.txt/.jpg/.png)"}
                    <input
                      hidden
                      type="file"
                      accept=".pdf,.docx,.pptx,.txt,.jpg,.jpeg,.png"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                  </Button>
                  <TextField
                    label="Topic (optional)"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    fullWidth
                  />
                  <Button onClick={handleUpload} variant="contained" disabled={loading.upload}>
                    {loading.upload ? "Uploading..." : "Upload & Extract"}
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Language & Input Context</Typography>
                  <FormControl fullWidth>
                    <InputLabel id="upload-label">Select Upload</InputLabel>
                    <Select
                      labelId="upload-label"
                      value={selectedUploadId}
                      label="Select Upload"
                      onChange={(e) =>
                        setSelectedUploadId(e.target.value === "" ? "" : Number(e.target.value))
                      }
                    >
                      <MenuItem value="">Manual text only</MenuItem>
                      {history.map((item) => (
                        <MenuItem key={item.id} value={item.id}>
                          {item.original_filename}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth>
                    <InputLabel id="lang-label">Target Language</InputLabel>
                    <Select
                      labelId="lang-label"
                      value={language}
                      label="Target Language"
                      onChange={(e) => setLanguage(e.target.value)}
                    >
                      {LANGUAGES.map((lang) => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={enableVoice}
                        onChange={(e) => setEnableVoice(e.target.checked)}
                      />
                    }
                    label="Enable voice output (gTTS)"
                  />
                  <TextField
                    label="Manual context text (optional)"
                    value={manualText}
                    onChange={(e) => setManualText(e.target.value)}
                    multiline
                    minRows={3}
                  />
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Translation</Typography>
                  <Button
                    variant="contained"
                    startIcon={<TranslateRoundedIcon />}
                    onClick={handleTranslate}
                    disabled={loading.translate}
                  >
                    {loading.translate ? "Translating..." : "Translate Text"}
                  </Button>
                  <Paper variant="outlined" sx={{ p: 2, minHeight: 110 }}>
                    <Typography variant="body2" color="text.secondary">
                      {translatedText || "Translated text appears here."}
                    </Typography>
                  </Paper>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Summary Generator</Typography>
                  <Button
                    variant="contained"
                    startIcon={<AutoAwesomeRoundedIcon />}
                    onClick={handleSummary}
                    disabled={loading.summary}
                  >
                    {loading.summary ? "Generating..." : "Generate Summary"}
                  </Button>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2">Short Summary</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {summary?.short_summary || "No summary yet."}
                    </Typography>
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>
                      Bullet Points
                    </Typography>
                    <List dense>
                      {(summary?.bullet_points || []).map((point, idx) => (
                        <ListItem key={`${idx}-${point}`} sx={{ px: 0 }}>
                          <ListItemText primary={`• ${point}`} />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">AI Questions</Typography>
                  <Button
                    variant="contained"
                    startIcon={<QuizRoundedIcon />}
                    onClick={handleQuestions}
                    disabled={loading.questions}
                  >
                    {loading.questions ? "Generating..." : "Generate Questions"}
                  </Button>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2">Short-answer (5)</Typography>
                    <List dense>
                      {(questions?.short_answer_questions || []).map((item, idx) => (
                        <ListItem key={`${idx}-${item}`} sx={{ px: 0 }}>
                          <ListItemText primary={`${idx + 1}. ${item}`} />
                        </ListItem>
                      ))}
                    </List>
                    <Typography variant="subtitle2">MCQs (5)</Typography>
                    <List dense>
                      {(questions?.mcqs || []).map((mcq, idx) => (
                        <ListItem key={`${idx}-${mcq.question}`} sx={{ px: 0 }}>
                          <ListItemText
                            primary={`${idx + 1}. ${mcq.question}`}
                            secondary={mcq.options?.join(" | ")}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Context-Aware Chatbot</Typography>
                  <Paper variant="outlined" sx={{ p: 2, height: 260, overflowY: "auto" }}>
                    {chatMessages.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        Ask questions about the selected document.
                      </Typography>
                    ) : (
                      chatMessages.map((msg, idx) => (
                        <Box
                          key={`${idx}-${msg.role}`}
                          sx={{
                            mb: 1.2,
                            p: 1.2,
                            borderRadius: 1.5,
                            bgcolor: msg.role === "user" ? "rgba(20,184,166,0.12)" : "#f8fafc",
                            border: "1px solid #e2e8f0",
                          }}
                        >
                          <Typography variant="caption" color="text.secondary">
                            {msg.role.toUpperCase()}
                          </Typography>
                          <Typography variant="body2">{msg.content}</Typography>
                        </Box>
                      ))
                    )}
                  </Paper>
                  <Stack direction="row" spacing={1}>
                    <TextField
                      fullWidth
                      placeholder="Ask from document context..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                    />
                    <Button
                      variant="contained"
                      onClick={handleChatSend}
                      disabled={loading.chat}
                      endIcon={<SendRoundedIcon />}
                    >
                      Send
                    </Button>
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Voice Playback</Typography>
                  {audioUrl ? (
                    <audio controls src={audioUrl} style={{ width: "100%" }}>
                      Your browser does not support audio playback.
                    </audio>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Enable voice output and run translation/summary to generate audio.
                    </Typography>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Stack spacing={2}>
                  <Typography variant="h6">Learning Analytics</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {(analytics?.topics_learned || []).map((item) => (
                      <Chip key={item} label={item} sx={{ mb: 1 }} />
                    ))}
                    {!analytics?.topics_learned?.length ? (
                      <Typography variant="body2" color="text.secondary">
                        Topics will appear as you upload and summarize content.
                      </Typography>
                    ) : null}
                  </Stack>
                  <Typography variant="subtitle2">Recent Upload History</Typography>
                  <List dense>
                    {(analytics?.recent_uploads || []).map((item) => (
                      <ListItem key={item.id} sx={{ px: 0 }}>
                        <ListItemText
                          primary={`${item.original_filename} (${item.file_type.toUpperCase()})`}
                          secondary={new Date(item.created_at).toLocaleString()}
                        />
                      </ListItem>
                    ))}
                    {!analytics?.recent_uploads?.length ? (
                      <Typography variant="body2" color="text.secondary">
                        No uploads yet.
                      </Typography>
                    ) : null}
                  </List>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {selectedUpload ? (
          <Alert severity="info">
            Active context: <strong>{selectedUpload.original_filename}</strong>
          </Alert>
        ) : null}

        <Stack spacing={2}>
          <Typography variant="h6">Learn New Language</Typography>
          <Grid container spacing={2}>
            {learnLanguageCards.map((item) => (
              <Grid item xs={12} sm={6} md={3} key={item.code}>
                <LanguageLearningCard
                  language={item.language}
                  progress={item.progress}
                  xp={item.xp}
                  streak={item.streak}
                  level={item.level}
                  rewards={item.rewards}
                  onStart={() => handleStartLanguageLesson(item)}
                />
              </Grid>
            ))}
          </Grid>
        </Stack>
      </Stack>
    </DashboardLayout>
  );
}

export default DashboardPage;
