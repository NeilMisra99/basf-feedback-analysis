/** Audio manager for controlled playback with cleanup and error handling. */

export interface AudioState {
  feedbackId: string | null;
  isPlaying: boolean;
  currentTime?: number;
  duration?: number;
}

type AudioStateListener = (state: AudioState) => void;

export class AudioManager {
  private static instance: AudioManager;
  private currentAudio: HTMLAudioElement | null = null;
  private currentFeedbackId: string | null = null;
  private listeners: Set<AudioStateListener> = new Set();
  private audioPreloadCache: Map<string, HTMLAudioElement> = new Map();

  static getInstance(): AudioManager {
    if (!AudioManager.instance) {
      AudioManager.instance = new AudioManager();
    }
    return AudioManager.instance;
  }

  private constructor() {
    if (typeof window !== "undefined") {
      window.addEventListener("beforeunload", this.cleanup.bind(this));
    }
  }

  subscribe(callback: AudioStateListener): () => void {
    this.listeners.add(callback);
    callback(this.getCurrentState());
    return () => this.listeners.delete(callback);
  }

  private notify(): void {
    const state = this.getCurrentState();
    this.listeners.forEach((callback) => {
      try {
        callback(state);
      } catch (error) {
        console.error("Error in audio state listener:", error);
      }
    });
  }

  private getCurrentState(): AudioState {
    return {
      feedbackId: this.currentFeedbackId,
      isPlaying: this.isCurrentlyPlaying(),
      currentTime: this.currentAudio?.currentTime,
      duration: this.currentAudio?.duration,
    };
  }

  private isCurrentlyPlaying(): boolean {
    return this.currentAudio !== null && !this.currentAudio.paused;
  }

  async preloadAudio(_feedbackId: string, audioUrl: string): Promise<void> {
    if (this.audioPreloadCache.has(audioUrl)) {
      return;
    }

    const audio = new Audio();
    audio.preload = "metadata";
    audio.src = audioUrl;

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error("Audio preload timeout"));
      }, 5000);

      audio.onloadedmetadata = () => {
        clearTimeout(timeout);
        this.audioPreloadCache.set(audioUrl, audio);
        resolve();
      };

      audio.onerror = () => {
        clearTimeout(timeout);
        reject(new Error("Failed to preload audio"));
      };
    });
  }

  async playAudio(feedbackId: string, audioUrl: string): Promise<void> {
    try {
      this.audioPreloadCache.forEach((element) => {
        if (!element.paused) {
          element.pause();
          element.currentTime = 0;
        }
      });

      this.stopCurrent();

      let audio = this.audioPreloadCache.get(audioUrl);

      if (!audio) {
        audio = new Audio(audioUrl);
        this.audioPreloadCache.set(audioUrl, audio);
      } else {
        if (audio.src !== audioUrl) {
          audio.src = audioUrl;
        }
      }

      this.currentAudio = audio;
      this.currentFeedbackId = feedbackId;

      this.setupAudioEventListeners(audio);

      this.notify();

      await this.startPlayback(audio);
      this.notify();
    } catch (error) {
      this.cleanup();
      throw error;
    }
  }

  private setupAudioEventListeners(audio: HTMLAudioElement): void {
    audio.onplay = null;
    audio.onpause = null;
    audio.onended = null;
    audio.onerror = null;
    audio.ontimeupdate = null;

    audio.onplay = () => this.notify();
    audio.onpause = () => this.notify();

    audio.onended = () => {
      this.cleanup();
      this.notify();
    };

    audio.onerror = () => {
      this.cleanup();
      this.notify();
    };

    let lastUpdateTime = 0;
    audio.ontimeupdate = () => {
      const now = Date.now();
      if (now - lastUpdateTime > 1000) {
        lastUpdateTime = now;
        this.notify();
      }
    };
  }

  private startPlayback(audio: HTMLAudioElement): Promise<void> {
    return new Promise((resolve, reject) => {
      const playPromise = audio.play();

      if (playPromise !== undefined) {
        playPromise
          .then(() => resolve())
          .catch((error) => {
            console.error("Audio play failed:", error);
            reject(new Error("Failed to start audio playback"));
          });
      } else {
        resolve();
      }
    });
  }

  pauseAudio(feedbackId: string): void {
    if (this.currentFeedbackId === feedbackId && this.currentAudio) {
      this.currentAudio.pause();
      this.notify();
    }
  }

  resumeAudio(feedbackId: string): void {
    if (this.currentFeedbackId === feedbackId && this.currentAudio) {
      this.startPlayback(this.currentAudio)
        .then(() => this.notify())
        .catch(() => {
          this.cleanup();
          this.notify();
        });
    }
  }

  stopAudio(feedbackId: string): void {
    if (this.currentFeedbackId === feedbackId) {
      this.stopCurrent();
      this.notify();
    }
  }

  private stopCurrent(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.notify();
    }
  }

  getCurrentPlayingId(): string | null {
    return this.currentFeedbackId;
  }

  isPlaying(feedbackId: string): boolean {
    return this.currentFeedbackId === feedbackId && this.isCurrentlyPlaying();
  }

  private cleanup(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.src = "";
      this.currentAudio.load();
      for (const [url, element] of this.audioPreloadCache.entries()) {
        if (element === this.currentAudio) {
          this.audioPreloadCache.delete(url);
          break;
        }
      }
    }
    this.currentAudio = null;
    this.currentFeedbackId = null;
  }

  clearCache(): void {
    this.audioPreloadCache.forEach((audio) => {
      audio.pause();
      audio.src = "";
      audio.load();
    });
    this.audioPreloadCache.clear();
  }

  destroy(): void {
    this.cleanup();
    this.clearCache();
    this.listeners.clear();
  }
}

export const audioManager = AudioManager.getInstance();
