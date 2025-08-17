/** Audio state helpers for controls. */

export interface AudioControlState {
  isPlaying: boolean;
  isLoading: boolean;
  currentId: string | null;
}

export function getAudioButtonState(
  feedbackId: string,
  audioState: { feedbackId: string | null; isPlaying: boolean },
  audioLoading: boolean
): AudioControlState {
  const isCurrentlyPlaying =
    audioState.feedbackId === feedbackId && audioState.isPlaying;

  return {
    isPlaying: isCurrentlyPlaying,
    isLoading: audioLoading && audioState.feedbackId === feedbackId,
    currentId: audioState.feedbackId,
  };
}

export function getAudioButtonLabel(state: AudioControlState): string {
  if (state.isLoading) return "Loading";
  if (state.isPlaying) return "Pause";
  return "Play";
}
