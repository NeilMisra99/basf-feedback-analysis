/** Server-Sent Events client for real-time feedback updates. */

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

  connect(): void {
    if (this.isConnected || this.eventSource) {
      return;
    }

    try {
      this.eventSource = new EventSource(`${this.apiUrl}/events`);

      this.eventSource.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.lastEventAt = Date.now();
        this.startWatchdog();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data: SSEEvent = JSON.parse(event.data);
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

        this.handleReconnect();
      };
    } catch (error) {
      console.error("[SSE] Failed to create connection:", error);
      this.handleReconnect();
    }
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.stopWatchdog();
  }

  addEventListener(handler: SSEEventHandler): () => void {
    this.eventHandlers.add(handler);

    return () => {
      this.eventHandlers.delete(handler);
    };
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  waitForConnection(timeout: number = 5000): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnected) {
        resolve();
        return;
      }

      const checkInterval = 50;
      let elapsed = 0;

      const intervalId = setInterval(() => {
        if (this.isConnected) {
          clearInterval(intervalId);
          resolve();
        } else if (elapsed >= timeout) {
          clearInterval(intervalId);
          reject(new Error("SSE connection timeout"));
        }
        elapsed += checkInterval;
      }, checkInterval);
    });
  }

  private handleReconnect(): void {
    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );

    setTimeout(() => {
      this.disconnect(); // Clean up before reconnecting
      this.connect();
    }, delay);
  }

  private startWatchdog(): void {
    if (this.watchdogTimerId !== null) return;
    // Force reconnect on inactivity >90s (backend heartbeat ~15s)
    this.watchdogTimerId = window.setInterval(() => {
      const now = Date.now();
      if (this.eventSource && now - this.lastEventAt > 90000) {
        if (import.meta.env.DEV) {
          console.warn(
            "[SSE] Watchdog detected inactivity >90s. Reconnecting..."
          );
        }
        this.handleReconnect();
      }
    }, 45000);
  }

  private stopWatchdog(): void {
    if (this.watchdogTimerId !== null) {
      window.clearInterval(this.watchdogTimerId);
      this.watchdogTimerId = null;
    }
  }
}

export const sseService = new SSEService();
