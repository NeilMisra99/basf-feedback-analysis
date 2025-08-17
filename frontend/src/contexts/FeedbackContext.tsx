import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { sseService, type SSEEvent } from "../services/sseService";
import type { Feedback } from "../types";

interface FeedbackContextType {
  latestFeedback: Feedback | null;
  triggerRefresh: () => void;
  refreshTrigger: number;
}

const FeedbackContext = createContext<FeedbackContextType | undefined>(
  undefined
);

export function FeedbackProvider({ children }: { children: ReactNode }) {
  const [latestFeedback, setLatestFeedback] = useState<Feedback | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  useEffect(() => {
    const handleSSEEvent = (event: SSEEvent) => {
      switch (event.type) {
        case "feedback_update":
          if (event.data) {
            setLatestFeedback(event.data);
            // Components consume SSE updates directly; avoid global refresh
          }
          break;
        case "connected":
          break;
        case "heartbeat":
          break;
      }
    };

    sseService.connect();
    const removeListener = sseService.addEventListener(handleSSEEvent);

    return () => {
      removeListener();
      sseService.disconnect();
    };
  }, []);

  return (
    <FeedbackContext.Provider
      value={{ latestFeedback, triggerRefresh, refreshTrigger }}
    >
      {children}
    </FeedbackContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useFeedback() {
  const context = useContext(FeedbackContext);
  if (context === undefined) {
    throw new Error("useFeedback must be used within a FeedbackProvider");
  }
  return context;
}
