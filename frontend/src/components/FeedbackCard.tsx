import { useState, useEffect } from "react";
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
  AlertCircle,
  CheckCircle,
  Download,
} from "lucide-react";
import type { Feedback } from "../types";
import { feedbackAPI } from "../services/api";
import { audioManager, type AudioState } from "../services/audioManager";

interface FeedbackCardProps {
  feedback: Feedback;
}

export default function FeedbackCard({ feedback }: FeedbackCardProps) {
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
  const isCurrentlyPlaying =
    audioState.feedbackId === feedback.id && audioState.isPlaying;

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return <Smile className="h-4 w-4" />;
      case "negative":
        return <Frown className="h-4 w-4" />;
      default:
        return <Meh className="h-4 w-4" />;
    }
  };

  const getSentimentClassNames = (sentiment: string): string => {
    switch (sentiment) {
      case "positive":
        return "bg-green-100 text-green-800 border-green-200";
      case "negative":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const toggleAudio = async () => {
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
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getProcessingStatusDisplay = () => {
    switch (feedback.processing_status) {
      case "processing":
        return {
          icon: <Loader2 className="h-4 w-4 animate-spin" />,
          text: "Processing...",
          className: "bg-blue-100 text-blue-800 border-blue-200",
        };
      case "completed":
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          text: "Completed",
          className: "bg-green-100 text-green-800 border-green-200",
        };
      case "failed":
        return {
          icon: <AlertCircle className="h-4 w-4" />,
          text: "Failed",
          className: "bg-red-100 text-red-800 border-red-200",
        };
      default:
        return null;
    }
  };

  const maxLength = 200;
  const shouldShowExpand = feedback.text.length > maxLength;

  const displayText =
    shouldShowExpand && !isExpanded
      ? feedback.text.substring(0, maxLength) + "..."
      : feedback.text;

  return (
    <Card className="transition-colors rounded-lg shadow-none">
      <CardContent className="px-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Header with category, processing status, and date */}
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-white text-black">{feedback.category}</Badge>
              {getProcessingStatusDisplay() && (
                <Badge
                  className={`gap-1 ${getProcessingStatusDisplay()?.className}`}
                >
                  {getProcessingStatusDisplay()?.icon}
                  {getProcessingStatusDisplay()?.text}
                </Badge>
              )}
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatDate(feedback.created_at)}
              </div>
            </div>

            {/* Feedback Text */}
            <div className="mb-2">
              <p className="text-sm text-foreground">{displayText}</p>

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

            {/* Sentiment Analysis - only show when processing is completed */}
            {feedback.sentiment_analysis &&
              feedback.processing_status === "completed" && (
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

            {/* AI Response - only show when processing is completed */}
            {feedback.ai_response &&
              feedback.processing_status === "completed" && (
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

          {/* Audio Player - only show when processing is completed */}
          {feedback.audio_file &&
            feedback.processing_status === "completed" && (
              <div className="flex-shrink-0 flex gap-2">
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
                  {audioLoading
                    ? "Loading"
                    : isCurrentlyPlaying
                      ? "Pause"
                      : "Play"}
                </Button>
                <Button
                  onClick={() => {
                    if (feedback.audio_file) {
                      const audioUrl =
                        feedbackAPI.getAudioUrl(feedback.audio_file.id) +
                        "?download=true";
                      window.open(audioUrl, "_blank");
                    }
                  }}
                  variant="outline"
                  size="sm"
                  className="gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download
                </Button>
              </div>
            )}
        </div>
      </CardContent>
    </Card>
  );
}
