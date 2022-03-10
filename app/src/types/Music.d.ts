import { FILE_TYPE } from '../utils/enums';

declare global {
	interface MusicForm {
		fileType: keyof typeof FILE_TYPE;
		youtubeUrl: string;
		filename: string;
		artworkUrl: string;
		title: string;
		artist: string;
		album: string;
		grouping: string;
	}

	interface Job
		extends Pick<MusicForm, 'youtubeUrl' | 'filename' | 'artworkUrl' | 'title' | 'artist' | 'album' | 'grouping'> {
		id: string;
		completed: boolean;
		failed: boolean;
	}

	interface JobsResponse {
		jobs: Job[];
	}

	interface TagsResponse {
		artworkUrl: string;
		title: string;
		artist: string;
		album: string;
		grouping: string;
	}
}
