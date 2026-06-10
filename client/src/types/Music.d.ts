type MusicFormState =
  | {
      isFile: true;
      videoUrl: string;
      file: File;
      jobId?: string;
      uploadKey?: string;
      artworkUrl: string;
      resolvedArtworkUrl: string;
      title: string;
      artist: string;
      album: string;
      grouping?: string;
      uploadToWebdav: boolean;
    }
  | {
      isFile: false;
      videoUrl: string;
      file: null;
      artworkUrl: string;
      resolvedArtworkUrl: string;
      title: string;
      artist: string;
      album: string;
      grouping?: string;
      uploadToWebdav: boolean;
    };
