import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Pagination } from "@/components/ui/pagination";
import { MessageSquare, RefreshCw, Loader2 } from "lucide-react";
import FeedbackCard from "./FeedbackCard";
import {
  DashboardSkeleton,
  FeedbackCardSkeleton,
  StatCardSkeleton,
} from "./ui/loading";
import { StatCards } from "./stat-cards";
import { useDashboard } from "../hooks/use-dashboard";

export default function Dashboard() {
  const {
    stats,
    statsLoading,
    statsError,
    feedback,
    feedbackLoading,
    feedbackError,
    currentPage,
    pagination,
    isRefreshing,
    rangeText,
    handlePageChange,
    handleRefresh,
    reloadFeedback,
  } = useDashboard();

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
      <div className="flex-shrink-0 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statsLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : stats ? (
            <StatCards stats={stats} />
          ) : null}
        </div>
      </div>

      <div className="flex-shrink-0 mb-4">
        <div className="flex items-center justify-between pr-2">
          <div>
            <h2 className="text-lg font-semibold">All Feedback</h2>
            <p className="text-sm text-muted-foreground">{rangeText}</p>
          </div>
          <Button
            onClick={handleRefresh}
            variant="outline"
            className="!bg-white !text-black border-gray-300 shadow-none"
            disabled={isRefreshing || !feedback || feedback.length === 0}
          >
            {isRefreshing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="max-h-[500px] overflow-y-auto pr-2">
          <div className="space-y-2">
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
                  onClick={() => reloadFeedback(currentPage)}
                  variant="outline"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
              </div>
            ) : feedbackLoading ? (
              <>
                {Array.from({ length: 5 }).map((_, i) => (
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

      {pagination && pagination.pages > 1 ? (
        <div className="flex-shrink-0 mt-4">
          <Pagination
            currentPage={currentPage}
            totalPages={pagination.pages}
            onPageChange={handlePageChange}
            disabled={feedbackLoading}
          />
        </div>
      ) : null}
    </div>
  );
}
