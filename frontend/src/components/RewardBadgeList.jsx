import { Chip, Stack, Typography } from "@mui/material";

function RewardBadgeList({ rewards = [], emptyText = "No rewards yet." }) {
  if (!rewards.length) {
    return (
      <Typography variant="body2" color="text.secondary">
        {emptyText}
      </Typography>
    );
  }

  return (
    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
      {rewards.map((reward) => (
        <Chip key={reward} label={reward} size="small" />
      ))}
    </Stack>
  );
}

export default RewardBadgeList;
