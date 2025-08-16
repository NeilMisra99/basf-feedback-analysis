export interface Feedback {
  id: string;
  text: string;
  category: string;
  processing_status: "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
  sentiment_analysis?: SentimentAnalysis;
  ai_response?: AIResponse;
  audio_file?: AudioFile;
  audio_url?: string;
}

export interface SentimentAnalysis {
  id: string;
  feedback_id: string;
  sentiment: "positive" | "negative" | "neutral";
  confidence_score: number;
  processed_at: string;
}

export interface AIResponse {
  id: string;
  feedback_id: string;
  response_text: string;
  model_used: string;
  generated_at: string;
}

export interface AudioFile {
  id: string;
  feedback_id: string;
  file_path: string;
  duration_seconds: number;
  created_at: string;
}

export interface FeedbackSubmission {
  text: string;
  category: string;
}

export interface APIResponse<T> {
  status: "success" | "error";
  data?: T;
  message?: string;
  timestamp?: string;
}

export interface DashboardStats {
  total_feedback: number;
  sentiment_breakdown: {
    positive?: number;
    negative?: number;
    neutral?: number;
  };
  recent_feedback: Feedback[];
}

export interface PaginationInfo {
  page: number;
  pages: number;
  per_page: number;
  total: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedFeedbackResponse {
  data: Feedback[];
  pagination: PaginationInfo;
  filters?: {
    category?: string;
  };
}
