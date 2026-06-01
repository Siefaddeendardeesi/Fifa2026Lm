import axios, { AxiosError } from "axios";
import type { ApiError } from "@/lib/types/api";

const baseURL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (!error.response) {
      return Promise.reject(
        new Error(
          `Cannot reach the API at ${baseURL}. Start the backend (Docker: cd docker && docker compose up -d, or: uvicorn app.api.main:app --port 8000).`
        )
      );
    }
    const message =
      error.response?.data?.error ??
      error.message ??
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);
