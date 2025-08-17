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
  private reconnectDelay = 1000;
  private eventHandlers: Set<SSEEventHandler> = new Set();
  private watchdogTimerId: number | null = null;
  private lastEventAt = 0;

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

    if (import.meta.env.DEV) {
      console.log(`[SSE] Connecting to ${this.apiUrl}/events`);
    }

    try {
      this.eventSource = new EventSource(`${this.apiUrl}/events`);

      this.eventSource.onopen = () => {
        if (import.meta.env.DEV) {
          console.log("[SSE] Connection opened successfully");
        }
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.lastEventAt = Date.now();
        this.startWatchdog();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data: SSEEvent = JSON.parse(event.data);
          if (import.meta.env.DEV) {
            console.log("[SSE] Received event:", data.type, data);
          }
          this.lastEventAt = Date.now();
          this.reconnectAttempts = 0;

          this.eventHandlers.forEach((handler) => {
            try {
              handler(data);
            } catch (error) {
              console.error("[SSE] Error in event handler:", error);
            }
          });
        } catch (error) {
          if (import.meta.env.DEV) {
            console.error("[SSE] Error parsing data:", error, event.data);
          }
        }
      };

      this.eventSource.onerror = (error) => {
        if (import.meta.env.DEV) {
          console.error("[SSE] Connection error:", error);
        }
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
    this.stopWatchdog();
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

  private startWatchdog(): void {
    if (this.watchdogTimerId !== null) return;
    // Check every 30s; if no event within 60s, force reconnect
    this.watchdogTimerId = window.setInterval(() => {
      const now = Date.now();
      if (this.eventSource && now - this.lastEventAt > 60000) {
        if (import.meta.env.DEV) {
          console.warn(
            "[SSE] Watchdog detected inactivity >60s. Reconnecting..."
          );
        }
        this.handleReconnect();
      }
    }, 30000);
  }

  private stopWatchdog(): void {
    if (this.watchdogTimerId !== null) {
      window.clearInterval(this.watchdogTimerId);
      this.watchdogTimerId = null;
    }
  }
}

// Export singleton instance
export const sseService = new SSEService();
