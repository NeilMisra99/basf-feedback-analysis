/**
 * Utility functions for feedback processing status display
 */

import { Loader2, CheckCircle, AlertCircle } from "lucide-react";
import type { ReactElement } from "react";

export type ProcessingStatus = "processing" | "completed" | "failed";

export interface ProcessingStatusDisplay {
  icon: ReactElement;
  text: string;
  className: string;
}

export function getProcessingStatusDisplay(status: ProcessingStatus): ProcessingStatusDisplay | null {
  switch (status) {
    case "processing":
      return {
        icon: <Loader2 className="h-4 w-4 animate-spin" />,
        text: "Processing...",
        className: "bg-blue-100 text-blue-800 border-blue-200",
      };
    case "completed":
      return {
        icon: <CheckCircle className="h-4 w-4" />,
        text: "Completed",
        className: "bg-green-100 text-green-800 border-green-200",
      };
    case "failed":
      return {
        icon: <AlertCircle className="h-4 w-4" />,
        text: "Failed",
        className: "bg-red-100 text-red-800 border-red-200",
      };
    default:
      return null;
  }
}