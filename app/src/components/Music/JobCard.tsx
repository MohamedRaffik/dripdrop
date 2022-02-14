import { useMemo, useCallback, useEffect } from 'react';
import { useRecoilValue, useSetRecoilState } from 'recoil';
import { FileDownload, CopyAll, Delete, Error } from '@mui/icons-material';
import {
	Card,
	Container,
	Stack,
	CardMedia,
	CardContent,
	Typography,
	CardActions,
	CircularProgress,
	ButtonGroup,
	Button,
} from '@mui/material';
import { jobAtom, jobsAtom, musicFormAtom } from '../../state/Music';
import { FILE_TYPE } from '../../utils/enums';
import Image from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';
import { typographyDefaultCSS } from '../../utils/helpers';

interface JobCardProps {
	id: string;
}

const JobCard = (props: JobCardProps) => {
	const setJobs = useSetRecoilState(jobsAtom);
	const setMusicForm = useSetRecoilState(musicFormAtom);

	const { id } = props;
	const job = useRecoilValue(jobAtom(id));

	const { filename, youtubeUrl, title, artist, album, grouping, artworkUrl, completed, failed } = job;

	const [downloadJob, downloadJobStatus] = useLazyFetch<Blob>();
	const [removeJob, removeJobStatus] = useLazyFetch();

	const copyJob = useCallback(() => {
		setMusicForm({
			title,
			artist,
			album,
			grouping: grouping || '',
			fileType: FILE_TYPE.YOUTUBE,
			youtubeUrl: youtubeUrl || '',
			filename: '',
			artworkUrl: artworkUrl || '',
			groupingLoading: false,
			tagsLoading: false,
		});
	}, [album, artist, artworkUrl, grouping, setMusicForm, title, youtubeUrl]);

	useEffect(() => {
		if (removeJobStatus.isSuccess) {
			setJobs((jobs) => jobs.filter((job) => job.id !== id));
		}
	}, [id, removeJobStatus.isSuccess, setJobs]);

	useEffect(() => {
		if (downloadJobStatus.isSuccess) {
			const response = downloadJobStatus.response;
			const data = downloadJobStatus.data;
			if (response) {
				const contentDisposition = response.headers['content-disposition'] || '';
				const groups = contentDisposition.match(/filename\*?=(?:utf-8''|")(.+)(?:"|;)?/);
				const filename = decodeURIComponent(groups && groups.length > 1 ? groups[1] : 'downloaded.mp3');
				const url = URL.createObjectURL(data);
				const a = document.createElement('a');
				a.href = url;
				a.download = filename;
				a.click();
			}
		}
	}, [downloadJobStatus.data, downloadJobStatus.isSuccess, downloadJobStatus.response]);

	return useMemo(
		() => (
			<Card>
				<Container sx={{ my: 1 }}>
					<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center">
						<CardMedia component="img" height="150" image={artworkUrl || Image} alt="artwork" />
						<CardContent sx={{ flex: 2 }}>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">ID:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{id}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Source:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{filename || youtubeUrl}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Title:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{title}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Artist:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{artist}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Album:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{album}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Grouping:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{grouping}
								</Typography>
							</Stack>
							<CardActions>
								{!completed && !failed ? <CircularProgress /> : null}
								<ButtonGroup variant="contained">
									{completed && !failed ? (
										<Button
											title="Download File"
											color="success"
											onClick={() => downloadJob({ url: `/music/jobs/download/${id}`, responseType: 'blob' })}
										>
											<FileDownload />
										</Button>
									) : null}
									{failed ? (
										<Button title="Job Failed / File Not Found" color="error">
											<Error />
										</Button>
									) : null}
									<Button title="Copy to Form" onClick={() => copyJob()}>
										<CopyAll />
									</Button>
									<Button
										title="Delete Job and File"
										color="error"
										onClick={() => removeJob({ url: `/music/jobs/delete/${id}`, method: 'DELETE' })}
									>
										<Delete />
									</Button>
								</ButtonGroup>
							</CardActions>
						</CardContent>
					</Stack>
				</Container>
			</Card>
		),
		[
			album,
			artist,
			artworkUrl,
			completed,
			copyJob,
			downloadJob,
			failed,
			filename,
			grouping,
			id,
			removeJob,
			title,
			youtubeUrl,
		]
	);
};

export default JobCard;
