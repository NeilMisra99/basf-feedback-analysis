/**
 * Server-Sent Events service for real-time feedback updates
 */

import type { Feedback } from "../types";

export interface SSEEvent {
  type: "connected" | "heartbeat" | "feedback_update";
  data?: Feedback;
  message?: string;
  timestamp?: number;
}

export type SSEEventHandler = (event: SSEEvent) => void;

class SSEService {
  private eventSource: EventSource | null = null;
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private eventHandlers: Set<SSEEventHandler> = new Set();

  private get apiUrl(): string {
    return process.env.REACT_APP_API_URL || "http://localhost:5001/api/v1";
  }

  /**
   * Start SSE connection
   */
  connect(): void {
    if (this.isConnected || this.eventSource) {
      return;
    }

    console.log(`[SSE] Connecting to ${this.apiUrl}/events`);

    try {
      this.eventSource = new EventSource(`${this.apiUrl}/events`);

      this.eventSource.onopen = () => {
        console.log("[SSE] Connection opened successfully");
        this.isConnected = true;
        this.reconnectAttempts = 0;
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data: SSEEvent = JSON.parse(event.data);
          console.log("[SSE] Received event:", data.type, data);

          this.eventHandlers.forEach((handler) => {
            try {
              handler(data);
            } catch (error) {
              console.error("[SSE] Error in event handler:", error);
            }
          });
        } catch (error) {
          console.error("[SSE] Error parsing data:", error, event.data);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error("[SSE] Connection error:", error);
        this.isConnected = false;

        // Attempt to reconnect
        this.handleReconnect();
      };
    } catch (error) {
      console.error("[SSE] Failed to create connection:", error);
      this.handleReconnect();
    }
  }

  /**
   * Disconnect from SSE stream
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.isConnected = false;
    this.reconnectAttempts = 0;
  }

  /**
   * Add event handler
   */
  addEventListener(handler: SSEEventHandler): () => void {
    this.eventHandlers.add(handler);

    // Return cleanup function
    return () => {
      this.eventHandlers.delete(handler);
    };
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Handle reconnection logic
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("[SSE] Max reconnection attempts reached. Giving up.");
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      30000
    ); // Cap at 30 seconds

    setTimeout(() => {
      this.disconnect(); // Clean up before reconnecting
      this.connect();
    }, delay);
  }
}

// Export singleton instance
export const sseService = new SSEService();
