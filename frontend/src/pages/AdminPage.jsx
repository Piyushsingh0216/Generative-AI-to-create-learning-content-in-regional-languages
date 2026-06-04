import { useEffect, useState } from "react";
import {
  Alert,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";
import StatCard from "../components/StatCard";
import api from "../services/api";

function AdminPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get("/admin/stats");
        setStats(response.data);
      } catch (err) {
        setError(err?.response?.data?.detail || "Failed to load admin stats.");
      }
    };
    load();
  }, []);

  return (
    <DashboardLayout>
      <Stack spacing={2.5}>
        <Typography variant="h5">Admin Panel</Typography>
        {error ? <Alert severity="error">{error}</Alert> : null}

        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <StatCard title="Total Users" value={stats?.total_users ?? 0} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <StatCard title="Total Uploads" value={stats?.total_uploads ?? 0} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <StatCard title="Total Summaries" value={stats?.total_summaries ?? 0} />
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              AI Usage Stats
            </Typography>
            <List dense>
              {Object.entries(stats?.ai_usage_by_action || {}).map(([action, count]) => (
                <ListItem key={action} sx={{ px: 0 }}>
                  <ListItemText
                    primary={action}
                    secondary={`Total requests: ${count}`}
                  />
                </ListItem>
              ))}
              {!Object.keys(stats?.ai_usage_by_action || {}).length ? (
                <Typography variant="body2" color="text.secondary">
                  No AI usage recorded yet.
                </Typography>
              ) : null}
            </List>
          </CardContent>
        </Card>
      </Stack>
    </DashboardLayout>
  );
}

export default AdminPage;
