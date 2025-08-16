import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Play,
  Pause,
  Loader2,
  Clock,
  ChevronDown,
  ChevronUp,
  Download,
} from "lucide-react";
import type { Feedback } from "../types";
import { feedbackAPI } from "../services/api";
import { audioManager, type AudioState } from "../services/audioManager";
import { getSentimentIcon, getSentimentClassNames, formatConfidenceScore } from "../lib/sentimentUtils";
import { getAudioButtonState, getAudioButtonLabel } from "../lib/audioUtils";
import { getProcessingStatusDisplay } from "../lib/processingUtils";

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

  const isProcessingCompleted = feedback.processing_status === "completed";

  useEffect(() => {
    const unsubscribe = audioManager.subscribe((state: AudioState) => {
      setAudioState(state);
      if (state.feedbackId === feedback.id || (state.isPlaying && state.feedbackId !== feedback.id)) {
        setAudioLoading(false);
      }
    });

    return unsubscribe;
  }, [feedback.id]);

  const audioButtonState = getAudioButtonState(feedback.id, audioState, audioLoading);
  const isCurrentlyPlaying = audioButtonState.isPlaying;

  const toggleAudio = async () => {
    if (!feedback.audio_file || !feedback.audio_url) return;

    try {
      if (isCurrentlyPlaying) {
        audioManager.pauseAudio(feedback.id);
      } else if (audioManager.getCurrentPlayingId() === feedback.id) {
        audioManager.resumeAudio(feedback.id);
      } else {
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

  const processingStatusDisplay = getProcessingStatusDisplay(feedback.processing_status as "processing" | "completed" | "failed");

  const maxLength = 200;
  const shouldShowExpand = feedback.text.length > maxLength;
  const displayText = shouldShowExpand && !isExpanded 
    ? `${feedback.text.substring(0, maxLength)}...` 
    : feedback.text;

  return (
    <Card className="transition-colors rounded-lg shadow-none">
      <CardContent className="px-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-white text-black">{feedback.category}</Badge>
              {processingStatusDisplay && (
                <Badge
                  className={`gap-1 ${processingStatusDisplay.className}`}
                >
                  <processingStatusDisplay.icon 
                    className={`h-4 w-4 ${feedback.processing_status === 'processing' ? 'animate-spin' : ''}`} 
                  />
                  {processingStatusDisplay.text}
                </Badge>
              )}
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatDate(feedback.created_at)}
              </div>
            </div>

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

            {feedback.sentiment_analysis && isProcessingCompleted && (
                <div className="flex items-center gap-2 mb-2">
                  <Badge
                    className={`gap-1 ${getSentimentClassNames(
                      feedback.sentiment_analysis.sentiment
                    )}`}
                  >
                    {(() => {
                      const IconComponent = getSentimentIcon(feedback.sentiment_analysis.sentiment);
                      return <IconComponent className="h-4 w-4" />;
                    })()}
                    {feedback.sentiment_analysis.sentiment}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {formatConfidenceScore(feedback.sentiment_analysis.confidence_score)}
                  </span>
                </div>
              )}

            {feedback.ai_response && isProcessingCompleted && (
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

          {feedback.audio_file && isProcessingCompleted && (
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
                  {getAudioButtonLabel(audioButtonState)}
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
