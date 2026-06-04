import { Button, Card, CardContent, LinearProgress, Stack, Typography } from "@mui/material";

import RewardBadgeList from "./RewardBadgeList";

function LanguageLearningCard({ language, progress, xp, streak, level, rewards, onStart }) {
  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">{language}</Typography>
          <Typography variant="body2" color="text.secondary">
            Level: {level}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            XP: {xp}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Daily streak: {streak} days
          </Typography>
          <Stack spacing={0.6}>
            <Typography variant="body2" color="text.secondary">
              Progress to next level: {progress}%
            </Typography>
            <LinearProgress variant="determinate" value={progress} />
          </Stack>
          <Stack spacing={0.6}>
            <Typography variant="body2" color="text.secondary">
              Rewards
            </Typography>
            <RewardBadgeList rewards={rewards} />
          </Stack>
          <Button variant="contained" onClick={onStart}>
            Start
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default LanguageLearningCard;
