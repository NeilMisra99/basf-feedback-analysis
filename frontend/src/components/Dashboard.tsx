import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  MessageSquare,
  TrendingUp,
  TrendingDown,
  RefreshCw,
} from "lucide-react";
import { feedbackAPI } from "../services/api";
import { sseService, type SSEEvent } from "../services/sseService";
import type { Feedback, DashboardStats } from "../types";
import FeedbackCard from "./FeedbackCard";
import { DashboardSkeleton } from "./ui/loading";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load real dashboard data from API
      const statsResponse = await feedbackAPI.getDashboardStats();

      if (statsResponse.status === "success" && statsResponse.data) {
        setStats(statsResponse.data);
        setFeedback(statsResponse.data.recent_feedback || []);
      } else {
        throw new Error(
          statsResponse.message || "Failed to load dashboard data"
        );
      }
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : typeof err === "object" && err !== null && "message" in err
            ? String((err as { message: unknown }).message)
            : "Failed to load dashboard data";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []); // Only run once on mount

  // Setup SSE connection for real-time updates - delay until initial load is complete
  useEffect(() => {
    // Only start SSE after initial load is complete
    if (loading) return;
    const handleSSEEvent = (event: SSEEvent) => {
      switch (event.type) {
        case "feedback_update":
          if (event.data) {
            setFeedback((prevFeedback) => {
              const existingIndex = prevFeedback.findIndex(
                (f) => f.id === event.data!.id
              );

              if (existingIndex >= 0) {
                // Update existing feedback
                const updated = [...prevFeedback];
                updated[existingIndex] = event.data!;
                return updated;
              } else {
                // Add new feedback (insert at beginning to maintain chronological order)
                return [event.data!, ...prevFeedback.slice(0, 4)]; // Keep only 5 most recent
              }
            });

            // Update stats if needed
            if (event.data.processing_status === "completed") {
              // Refresh stats when feedback processing completes
              loadDashboardData();
            }
          }
          break;
        case "connected":
          break;
        case "heartbeat":
          // SSE connection is alive
          break;
      }
    };

    // Connect to SSE and add event listener
    sseService.connect();
    const removeListener = sseService.addEventListener(handleSSEEvent);

    // Cleanup on unmount
    return () => {
      removeListener();
      sseService.disconnect();
    };
  }, [loading]); // Only dependency is loading state

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <Card className="max-w-2xl mx-auto shadow-none">
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="text-destructive mb-4">
              <MessageSquare className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error Loading Dashboard</h3>
              <p className="text-sm text-muted-foreground mt-1">{error}</p>
            </div>
            <Button onClick={loadDashboardData} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Statistics Overview - Fixed at top */}
      {stats && (
        <div className="flex-shrink-0 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Total Feedback */}
            <Card className="p-4 shadow-none">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Total Feedback
                  </p>
                  <p className="text-2xl font-bold">{stats.total_feedback}</p>
                </div>
                <MessageSquare className="h-5 w-5 text-muted-foreground" />
              </div>
            </Card>

            {/* Positive Sentiment */}
            <Card className="p-4 shadow-none">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Positive
                  </p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.sentiment_breakdown.positive || 0}
                  </p>
                </div>
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
            </Card>

            {/* Negative Sentiment */}
            <Card className="p-4 shadow-none">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Negative
                  </p>
                  <p className="text-2xl font-bold text-red-600">
                    {stats.sentiment_breakdown.negative || 0}
                  </p>
                </div>
                <TrendingDown className="h-5 w-5 text-red-600" />
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Recent Feedback Title */}
      <div className="flex-shrink-0 mb-4">
        <h2 className="text-lg font-semibold">Recent Feedback</h2>
      </div>

      {/* Recent Feedback - Scrollable */}
      <div className="flex-1 overflow-hidden">
        <div className="max-h-[500px] overflow-y-auto pr-2">
          <div className="space-y-2">
            {feedback.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium text-muted-foreground mb-2">
                  No feedback yet
                </h3>
                <p className="text-sm text-muted-foreground">
                  Get started by submitting your first feedback.
                </p>
              </div>
            ) : (
              feedback.map((item) => (
                <FeedbackCard key={item.id} feedback={item} />
              ))
            )}
          </div>
        </div>
      </div>

      {/* Refresh Button - Fixed at bottom */}
      <div className="flex-shrink-0 flex justify-center mt-4 pt-4">
        <Button onClick={loadDashboardData} variant="default">
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>
    </div>
  );
}
