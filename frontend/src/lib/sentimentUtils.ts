import { Smile, Frown, Meh } from "lucide-react";

export type SentimentType = "positive" | "negative" | "neutral";

export function getSentimentIcon(sentiment: string) {
  switch (sentiment) {
    case "positive":
      return Smile;
    case "negative":
      return Frown;
    default:
      return Meh;
  }
}

export function getSentimentClassNames(sentiment: string): string {
  switch (sentiment) {
    case "positive":
      return "bg-green-100 text-green-800 border-green-200";
    case "negative":
      return "bg-red-100 text-red-800 border-red-200";
    default:
      return "bg-gray-100 text-gray-800 border-gray-200";
  }
}

export function formatConfidenceScore(score: number | undefined): string {
  return `${Math.round((score || 0) * 100)}% confidence`;
}