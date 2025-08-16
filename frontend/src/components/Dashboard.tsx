import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Pagination } from "@/components/ui/pagination";
import {
  MessageSquare,
  TrendingUp,
  TrendingDown,
  RefreshCw,
} from "lucide-react";
import { feedbackAPI } from "../services/api";
import { useFeedback } from "../contexts/FeedbackContext";
import type { Feedback, DashboardStats, PaginationInfo } from "../types";
import FeedbackCard from "./FeedbackCard";
import {
  DashboardSkeleton,
  FeedbackCardSkeleton,
  StatCardSkeleton,
} from "./ui/loading";
import { getErrorMessageWithFallback } from "../lib/errorUtils";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);

  // Pagination state
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  // Real-time updates
  const [, setStatsProcessedIds] = useState<Set<string>>(
    new Set()
  );
  const { latestFeedback, refreshTrigger } = useFeedback();

  const loadDashboardStats = async () => {
    try {
      setStatsLoading(true);
      setStatsError(null);

      const statsResponse = await feedbackAPI.getDashboardStats();
      if (statsResponse.status === "success" && statsResponse.data) {
        setStats(statsResponse.data);
      } else {
        throw new Error(
          statsResponse.message || "Failed to load dashboard stats"
        );
      }
    } catch (err: unknown) {
      setStatsError(
        getErrorMessageWithFallback(err, "Failed to load dashboard stats")
      );
    } finally {
      setStatsLoading(false);
    }
  };

  const loadFeedback = async (page: number = 1) => {
    try {
      setFeedbackLoading(true);
      setFeedbackError(null);
      setPagination(null); // Clear pagination during loading

      const response = await feedbackAPI.getAllFeedback(page, 5);
      if (response.status === "success") {
        // Backend returns { status, data: [...], pagination: {...} }
        setFeedback(response.data || []); // Ensure we always have an array
        setPagination(response.pagination || null);
        setCurrentPage(page);
      } else {
        throw new Error(response.message || "Failed to load feedback");
      }
    } catch (err: unknown) {
      setFeedbackError(
        getErrorMessageWithFallback(err, "Failed to load feedback")
      );
    } finally {
      setFeedbackLoading(false);
    }
  };

  const handlePageChange = (page: number) => {
    loadFeedback(page);
  };

  const handleRefresh = () => {
    loadDashboardStats();
    loadFeedback(currentPage);
    setStatsProcessedIds(new Set());
  };

  // Load data on mount and refresh
  useEffect(() => {
    if (refreshTrigger >= 0) {
      loadDashboardStats();
      loadFeedback(1);
    }
  }, [refreshTrigger]);

  // Handle real-time feedback updates via SSE
  useEffect(() => {
    if (!latestFeedback) return;

    // Always update the feedback list with the latest data
    setFeedback((prevFeedback) => {
      const existingIndex = prevFeedback.findIndex(f => f.id === latestFeedback.id);
      if (existingIndex >= 0) {
        // Update existing feedback item with latest status
        const updatedFeedback = [...prevFeedback];
        updatedFeedback[existingIndex] = latestFeedback;
        return updatedFeedback;
      } else {
        // Add new feedback at the beginning if it doesn't exist
        return [latestFeedback, ...prevFeedback];
      }
    });

    // Update stats only once when feedback completes
    if (latestFeedback.processing_status === "completed" && latestFeedback.sentiment_analysis) {
      setStatsProcessedIds((prevIds) => {
        // Check if we've already processed this feedback for stats
        if (prevIds.has(latestFeedback.id)) {
          return prevIds;
        }
        
        // Mark as processed
        const newIds = new Set(prevIds);
        newIds.add(latestFeedback.id);
        
        // Update stats
        setStats((prevStats) => {
          if (!prevStats) return prevStats;
          
          const sentiment = latestFeedback.sentiment_analysis!.sentiment;
          return {
            ...prevStats,
            total_feedback: prevStats.total_feedback + 1,
            sentiment_breakdown: {
              ...prevStats.sentiment_breakdown,
              [sentiment]: (prevStats.sentiment_breakdown[sentiment] || 0) + 1,
            },
          };
        });
        
        return newIds;
      });
    }
  }, [latestFeedback]);

  if (statsLoading && (!feedback || feedback.length === 0)) {
    return <DashboardSkeleton />;
  }

  if (statsError && !stats) {
    return (
      <Card className="max-w-2xl mx-auto shadow-none">
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="text-destructive mb-4">
              <MessageSquare className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error Loading Dashboard</h3>
              <p className="text-sm text-muted-foreground mt-1">{statsError}</p>
            </div>
            <Button onClick={handleRefresh} variant="outline">
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
      {/* Stats Cards */}
      <div className="flex-shrink-0 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {statsLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : stats ? (
            <>
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
            </>
          ) : null}
        </div>
      </div>

      {/* Feedback Section Header */}
      <div className="flex-shrink-0 mb-4">
        <div>
          <h2 className="text-lg font-semibold">All Feedback</h2>
          <p className="text-sm text-muted-foreground">
            {pagination && pagination.total > 0 &&
              `Showing ${(currentPage - 1) * pagination.per_page + 1}-${Math.min(currentPage * pagination.per_page, pagination.total)} of ${pagination.total} items`}
          </p>
        </div>
      </div>

      {/* Feedback List */}
      <div className="flex-1 overflow-hidden">
        <div className="max-h-[500px] overflow-y-auto pr-2">
          <div className="space-y-2 mb-6">
            {feedbackError ? (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h3 className="text-lg font-medium text-destructive mb-2">
                  Error Loading Feedback
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {feedbackError}
                </p>
                <Button
                  onClick={() => loadFeedback(currentPage)}
                  variant="outline"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
              </div>
            ) : feedbackLoading ? (
              <>
                {[...Array(5)].map((_, i) => (
                  <FeedbackCardSkeleton key={i} />
                ))}
              </>
            ) : feedback.length === 0 ? (
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

      {/* Pagination Controls */}
      <div className="flex-shrink-0 my-4">
        {pagination ? (
          <Pagination
            currentPage={currentPage}
            totalPages={pagination.pages}
            onPageChange={handlePageChange}
            disabled={feedbackLoading}
          />
        ) : null}
      </div>

      {/* Refresh Button */}
      <div className="flex-shrink-0 flex justify-center pt-4">
        <Button
          onClick={handleRefresh}
          variant="outline"
          className="!bg-white !text-black border-gray-300"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>
    </div>
  );
}
