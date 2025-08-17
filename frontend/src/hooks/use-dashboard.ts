import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { feedbackAPI } from "../services/api";
import { useFeedback } from "../contexts/FeedbackContext";
import { getErrorMessageWithFallback } from "../lib/errorUtils";
import type { Feedback, DashboardStats, PaginationInfo } from "../types";

interface UseDashboardResult {
  stats: DashboardStats | null;
  statsLoading: boolean;
  statsError: string | null;
  feedback: Feedback[];
  feedbackLoading: boolean;
  feedbackError: string | null;
  currentPage: number;
  pagination: PaginationInfo | null;
  isRefreshing: boolean;
  rangeText: string;
  handlePageChange: (page: number) => void;
  handleRefresh: () => Promise<void>;
  reloadFeedback: (page: number) => Promise<void>;
}

export function useDashboard(): UseDashboardResult {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);

  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  const { latestFeedback, refreshTrigger } = useFeedback();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const prevRefreshTriggerRef = useRef<number | null>(null);
  const prevLatestFeedbackIdRef = useRef<string | number | null>(null);
  const completedIdsRef = useRef<Set<string>>(new Set());

  const loadDashboardStats = useCallback(async () => {
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
  }, []);

  const loadFeedback = useCallback(async (page: number = 1) => {
    try {
      setFeedbackLoading(true);
      setFeedbackError(null);
      setPagination(null);

      const response = await feedbackAPI.getAllFeedback(page, 5);
      if (response.status === "success") {
        setFeedback(response.data || []);
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
  }, []);

  const handlePageChange = useCallback(
    (page: number) => {
      loadFeedback(page);
    },
    [loadFeedback]
  );

  const handleRefresh = useCallback(async () => {
    try {
      setIsRefreshing(true);
      await Promise.all([loadDashboardStats(), loadFeedback(currentPage)]);
    } finally {
      setIsRefreshing(false);
    }
  }, [currentPage, loadDashboardStats, loadFeedback]);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | null = null;

    if (refreshTrigger !== prevRefreshTriggerRef.current) {
      prevRefreshTriggerRef.current = refreshTrigger;
      if (refreshTrigger >= 0) {
        loadDashboardStats();
        loadFeedback(1);
      }
    }

    if (
      latestFeedback &&
      latestFeedback.id !== prevLatestFeedbackIdRef.current
    ) {
      prevLatestFeedbackIdRef.current = latestFeedback.id as unknown as
        | string
        | number;
      setFeedback((prevFeedback) => {
        const existingIndex = prevFeedback.findIndex(
          (f) => f.id === latestFeedback.id
        );
        if (existingIndex >= 0) {
          const updatedFeedback = [...prevFeedback];
          updatedFeedback[existingIndex] = latestFeedback;
          return updatedFeedback;
        }
        return [latestFeedback, ...prevFeedback];
      });
    }

    // Independently refresh stats once when an item completes processing
    if (
      latestFeedback &&
      latestFeedback.processing_status === "completed" &&
      !completedIdsRef.current.has(latestFeedback.id)
    ) {
      completedIdsRef.current.add(latestFeedback.id);
      loadDashboardStats();
    }

    const hasProcessingItems = feedback.some(
      (f) => f.processing_status === "processing"
    );
    if (hasProcessingItems) {
      timer = setTimeout(() => {
        loadFeedback(currentPage);
      }, 1000);
    }

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [
    refreshTrigger,
    latestFeedback,
    feedback,
    currentPage,
    loadDashboardStats,
    loadFeedback,
  ]);

  const rangeText = useMemo(() => {
    if (!pagination || pagination.total <= 0) return "";
    const start = (currentPage - 1) * pagination.per_page + 1;
    const end = Math.min(currentPage * pagination.per_page, pagination.total);
    return `Showing ${start}-${end} of ${pagination.total} items`;
  }, [pagination, currentPage]);

  return {
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
    reloadFeedback: loadFeedback,
  };
}
