import { useCallback, useEffect, useMemo } from 'react';
import {
	Card,
	Button,
	ButtonGroup,
	CardContent,
	Stack,
	CardMedia,
	SxProps,
	Theme,
	List,
	ListItem,
	ListItemText,
	CardActions,
	Box,
	CircularProgress,
} from '@mui/material';
import { Error } from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { useRemoveJobMutation, useLazyDownloadJobQuery } from '../../api';
import { FILE_TYPE } from '../../utils/enums';
import BlankImage from '../../images/blank_image.jpeg';
import { updateForm } from '../../state/music';
import { CopyAll, Delete, Download } from '@mui/icons-material';

interface JobCardProps {
	job: Job;
	sx?: SxProps<Theme>;
}

const JobCard = (props: JobCardProps) => {
	const { job, sx } = props;

	const [removeJob] = useRemoveJobMutation();
	const [downloadJob, downloadJobStatus] = useLazyDownloadJobQuery();

	const dispatch = useDispatch();

	const copyJob = useCallback(() => {
		dispatch(
			updateForm({
				...job,
				grouping: job.grouping || '',
				fileType: FILE_TYPE.YOUTUBE,
				youtubeUrl: job.youtubeUrl || '',
				filename: '',
				artworkUrl: job.artworkUrl || '',
			})
		);
	}, [dispatch, job]);

	useEffect(() => {
		const handleDownload = async (response: Response) => {
			const data = await response.blob();
			const contentDisposition = response.headers.get('content-disposition') || '';
			const groups = contentDisposition.match(/filename\*?=(?:utf-8''|")(.+)(?:"|;)?/);
			const filename = decodeURIComponent(groups && groups.length > 1 ? groups[1] : 'downloaded.mp3');
			const url = URL.createObjectURL(data);
			const a = document.createElement('a');
			a.href = url;
			a.download = filename;
			a.click();
		};
		if (downloadJobStatus.isSuccess) {
			handleDownload(downloadJobStatus.data);
		}
	}, [downloadJobStatus.data, downloadJobStatus.isSuccess]);

	const DownloadButton = useMemo(() => {
		if (!job.completed && !job.failed) {
			return (
				<Button>
					<CircularProgress />
				</Button>
			);
		} else if (!job.completed) {
			return (
				<Button color="error" disabled>
					<Error />
				</Button>
			);
		}
		return (
			<Button color="success" onClick={() => downloadJob(job.id)}>
				<Download />
			</Button>
		);
	}, [downloadJob, job.completed, job.failed, job.id]);

	return useMemo(
		() => (
			<Card sx={sx}>
				<Stack height="100%" alignItems="center">
					<CardMedia component="img" image={job.artworkUrl || BlankImage} />
					<CardContent>
						<List>
							<ListItem>
								<Stack>
									<ListItemText secondary="ID" />
									<ListItemText primary={job.id} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Source" />
									<ListItemText primary={job.filename || job.youtubeUrl} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Title" />
									<ListItemText primary={job.title} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Artist" />
									<ListItemText primary={job.artist} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Album" />
									<ListItemText primary={job.album} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Grouping" />
									<ListItemText primary={job.grouping || 'None'} />
								</Stack>
							</ListItem>
						</List>
					</CardContent>
					<Box flex={1} />
					<CardActions>
						<Stack direction="row" justifyContent="center">
							<ButtonGroup>
								{DownloadButton}
								<Button onClick={() => copyJob()}>
									<CopyAll />
								</Button>
								<Button color="error" onClick={() => removeJob(job.id)}>
									<Delete />
								</Button>
							</ButtonGroup>
						</Stack>
					</CardActions>
				</Stack>
			</Card>
		),
		[
			DownloadButton,
			copyJob,
			job.album,
			job.artist,
			job.artworkUrl,
			job.filename,
			job.grouping,
			job.id,
			job.title,
			job.youtubeUrl,
			removeJob,
			sx,
		]
	);
};

export default JobCard;
