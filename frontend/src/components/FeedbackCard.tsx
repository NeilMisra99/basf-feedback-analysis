import { useState, useEffect, memo, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Play,
  Pause,
  Loader2,
  Clock,
  Smile,
  Frown,
  Meh,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import type { Feedback } from "../types";
import { feedbackAPI } from "../services/api";
import { audioManager, type AudioState } from "../services/audioManager";

interface FeedbackCardProps {
  feedback: Feedback;
}

function FeedbackCard({ feedback }: FeedbackCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioState, setAudioState] = useState<AudioState>({
    feedbackId: null,
    isPlaying: false,
  });

  useEffect(() => {
    const unsubscribe = audioManager.subscribe((state: AudioState) => {
      setAudioState(state);
      
      // Update loading state based on audio state
      if (state.feedbackId === feedback.id) {
        setAudioLoading(false);
      } else if (state.isPlaying && state.feedbackId !== feedback.id) {
        setAudioLoading(false);
      }
    });

    return unsubscribe;
  }, [feedback.id]);

  // Memoize derived state
  const isCurrentlyPlaying = audioState.feedbackId === feedback.id && audioState.isPlaying;

  // Memoize icon components for better performance
  const getSentimentIcon = useCallback((sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return <Smile className="h-4 w-4" />;
      case "negative":
        return <Frown className="h-4 w-4" />;
      default:
        return <Meh className="h-4 w-4" />;
    }
  }, []);

  const getSentimentClassNames = useCallback((sentiment: string): string => {
    switch (sentiment) {
      case "positive":
        return "bg-green-100 text-green-800 border-green-200";
      case "negative":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  }, []);

  const toggleAudio = useCallback(async () => {
    if (!feedback.audio_file || !feedback.audio_url) return;

    try {
      if (isCurrentlyPlaying) {
        // Pause current audio
        audioManager.pauseAudio(feedback.id);
      } else if (audioManager.getCurrentPlayingId() === feedback.id) {
        // Resume the same audio that was paused
        audioManager.resumeAudio(feedback.id);
      } else {
        // Play new audio (this will stop any other playing audio)
        setAudioLoading(true);
        const audioUrl = feedbackAPI.getAudioUrl(feedback.audio_file.id);
        await audioManager.playAudio(feedback.id, audioUrl);
      }
    } catch (error) {
      setAudioLoading(false);
      console.error("Error with audio playback:", error);
      // Use a more user-friendly error notification instead of alert
      // In a real app, you'd use a toast notification system
      console.error("Failed to play audio file");
    }
  }, [feedback.id, feedback.audio_file, feedback.audio_url, isCurrentlyPlaying]);

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleString();
  }, []);

  const shouldShowExpand = feedback.text.length > 150;

  return (
    <Card className="transition-colors rounded-lg shadow-none">
      <CardContent className="px-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Header with category and date */}
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-white text-black">{feedback.category}</Badge>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatDate(feedback.created_at)}
              </div>
            </div>

            {/* Feedback Text */}
            <div className="mb-2">
              <p
                className={`text-sm text-foreground ${!isExpanded && shouldShowExpand ? "line-clamp-3" : ""}`}
              >
                {feedback.text}
              </p>

              {shouldShowExpand && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="mt-2 h-auto p-0 text-xs text-muted-foreground hover:text-foreground py-1"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="h-3 w-3 mr-1" />
                      Show less
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-3 w-3 mr-1" />
                      Show more
                    </>
                  )}
                </Button>
              )}
            </div>

            {/* Sentiment Analysis */}
            {feedback.sentiment_analysis && (
              <div className="flex items-center gap-2 mb-2">
                <Badge
                  className={`gap-1 ${getSentimentClassNames(
                    feedback.sentiment_analysis.sentiment
                  )}`}
                >
                  {getSentimentIcon(feedback.sentiment_analysis.sentiment)}
                  {feedback.sentiment_analysis.sentiment}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {Math.round(
                    (feedback.sentiment_analysis.confidence_score || 0) * 100
                  )}
                  % confidence
                </span>
              </div>
            )}

            {/* AI Response */}
            {feedback.ai_response && (
              <div className="rounded-lg p-2 bg-gray-50">
                <h4 className="text-sm font-medium text-foreground mb-1">
                  AI Response
                </h4>
                <p className="text-sm text-muted-foreground">
                  {feedback.ai_response.response_text}
                </p>
              </div>
            )}
          </div>

          {/* Audio Player */}
          {feedback.audio_file && (
            <div className="flex-shrink-0">
              <Button
                onClick={toggleAudio}
                disabled={audioLoading}
                variant="outline"
                size="sm"
                className="gap-2"
              >
                {audioLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : isCurrentlyPlaying ? (
                  <Pause className="h-4 w-4" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                {audioLoading ? "Loading" : isCurrentlyPlaying ? "Pause" : "Play"}
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default memo(FeedbackCard);
