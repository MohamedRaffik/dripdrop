type MusicFormState =
  | {
      isFile: true;
      videoUrl: string;
      file: File;
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
