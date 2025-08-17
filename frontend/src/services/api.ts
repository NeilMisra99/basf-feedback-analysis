import axios, { AxiosError } from "axios";
import type {
  Feedback,
  FeedbackSubmission,
  APIResponse,
  DashboardStats,
  PaginatedFeedbackResponse,
} from "../types";

export interface APIError {
  message: string;
  status?: number;
  code?: string;
}

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5001/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000,
});

export const feedbackAPI = {
  submitFeedback: async (
    feedback: FeedbackSubmission
  ): Promise<APIResponse<Feedback>> => {
    const response = await api.post<APIResponse<Feedback>>(
      "/feedback",
      feedback
    );
    return response.data;
  },

  getFeedback: async (id: string): Promise<APIResponse<Feedback>> => {
    const response = await api.get<APIResponse<Feedback>>(`/feedback/${id}`);
    return response.data;
  },

  getAllFeedback: async (
    page = 1,
    perPage = 5
  ): Promise<
    PaginatedFeedbackResponse & { status: string; message?: string }
  > => {
    const response = await api.get<
      PaginatedFeedbackResponse & { status: string; message?: string }
    >(`/feedback?page=${page}&per_page=${perPage}`);
    return response.data;
  },

  getDashboardStats: async (): Promise<APIResponse<DashboardStats>> => {
    const response =
      await api.get<APIResponse<DashboardStats>>("/dashboard/stats");
    return response.data;
  },

  getAudioUrl: (audioId: string): string => {
    return `${API_BASE_URL}/audio/${audioId}`;
  },

  healthCheck: async (): Promise<
    APIResponse<{ status: string; timestamp: string }>
  > => {
    const response =
      await api.get<APIResponse<{ status: string; timestamp: string }>>(
        "/health"
      );
    return response.data;
  },
};

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIResponse<unknown>>) => {
    const apiError: APIError = {
      message:
        error.response?.data?.message ||
        error.message ||
        "An unexpected error occurred",
      status: error.response?.status,
      code: error.code,
    };

    if (import.meta.env.DEV) {
      console.error("API Error:", apiError);
    }

    return Promise.reject(apiError);
  }
);

export default api;
