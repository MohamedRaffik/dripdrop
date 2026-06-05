import React, { forwardRef, useMemo } from "react";
import ReactPlayer from "react-player";

import { YoutubeVideoResponse as YoutubeVideo } from "../../api/generated/youtubeApi";
import { useAddYoutubeVideoWatchMutation } from "../../api/youtube";

export interface ProgressState {
  playedSeconds: number;
}

interface VideoPlayerProps {
  video: YoutubeVideo | null | undefined;
  playing?: boolean;
  onDuration?: (duration: number) => void;
  onEnd?: () => void;
  onReady?: () => void;
  onProgress?: (state: ProgressState) => void;
  onPlay?: () => void;
  onPause?: () => void;
  width?: string;
  height?: string;
  style?: React.CSSProperties;
}

const VideoPlayer = forwardRef<HTMLVideoElement, VideoPlayerProps>(
  ({ video, onDuration, onProgress, onEnd, onReady, onPlay, onPause, playing, height, width, style }, ref) => {
    const [watchVideo] = useAddYoutubeVideoWatchMutation();

    return useMemo(
      () => (
        <ReactPlayer
          ref={ref}
          style={style}
          height={height || "100%"}
          width={width || "100%"}
          playing={playing}
          controls={true}
          src={video?.id ? `https://www.youtube.com/watch?v=${video.id}` : undefined}
          onPlay={() => {
            if (onPlay) {
              onPlay();
            }
          }}
          onPause={() => {
            if (onPause) {
              onPause();
            }
          }}
          onReady={() => {
            if (onReady) {
              onReady();
            }
          }}
          onDurationChange={(event) => {
            const duration = event.currentTarget.duration;
            if (onDuration && Number.isFinite(duration)) {
              onDuration(duration);
            }
          }}
          onTimeUpdate={(event) => {
            const playedSeconds = event.currentTarget.currentTime;
            if (video) {
              if (onProgress) {
                onProgress({ playedSeconds });
              }
              if (playedSeconds > 20 && !video.watched) {
                watchVideo(video.id);
              }
            }
          }}
          onEnded={() => {
            if (onEnd) {
              onEnd();
            }
          }}
        />
      ),
      [ref, style, width, height, playing, video, onPlay, onPause, onReady, onDuration, onProgress, watchVideo, onEnd]
    );
  }
);

export default VideoPlayer;
