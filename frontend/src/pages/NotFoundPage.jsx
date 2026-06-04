import { Button, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <Stack
      spacing={2}
      sx={{ minHeight: "100vh", alignItems: "center", justifyContent: "center", p: 3 }}
    >
      <Typography variant="h4">404</Typography>
      <Typography color="text.secondary">Page not found.</Typography>
      <Button variant="contained" onClick={() => navigate("/dashboard")}>
        Go to Dashboard
      </Button>
    </Stack>
  );
}

export default NotFoundPage;
