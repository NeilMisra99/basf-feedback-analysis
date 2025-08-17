/** Helpers for processing status display. */

import { Loader2, CheckCircle, AlertCircle } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type ProcessingStatus = "processing" | "completed" | "failed";

export interface ProcessingStatusDisplay {
  icon: LucideIcon;
  text: string;
  className: string;
}

export function getProcessingStatusDisplay(
  status: ProcessingStatus
): ProcessingStatusDisplay | null {
  switch (status) {
    case "processing":
      return {
        icon: Loader2,
        text: "Processing...",
        className: "bg-blue-100 text-blue-800 border-blue-200",
      };
    case "completed":
      return {
        icon: CheckCircle,
        text: "Completed",
        className: "bg-green-100 text-green-800 border-green-200",
      };
    case "failed":
      return {
        icon: AlertCircle,
        text: "Failed",
        className: "bg-red-100 text-red-800 border-red-200",
      };
    default:
      return null;
  }
}
