import { useCallback, useEffect, useMemo } from 'react';
import { useSetAtom, useAtom } from 'jotai';
import { Button, Card, Container, Grid, Image, List } from 'semantic-ui-react';
import { jobsAtomState, musicFormAtom } from '../../state/Music';
import { FILE_TYPE } from '../../utils/enums';
import BlankImage from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

interface JobCardProps {
	job: Job;
}

const JobCard = (props: JobCardProps) => {
	const { job } = props;
	const [jobsState, setJobsState] = useAtom(jobsAtomState);
	const setMusicForm = useSetAtom(musicFormAtom);

	const [downloadJob, downloadJobStatus] = useLazyFetch<Blob>();
	const [removeJob, removeJobStatus] = useLazyFetch();

	const copyJob = useCallback(() => {
		if (job) {
			setMusicForm({
				...job,
				grouping: job.grouping || '',
				fileType: FILE_TYPE.YOUTUBE,
				youtubeUrl: job.youtubeUrl || '',
				filename: '',
				artworkUrl: job.artworkUrl || '',
			});
		}
	}, [job, setMusicForm]);

	useEffect(() => {
		const currentJobId = job.id;
		if (removeJobStatus.success) {
			setJobsState(jobsState.data.jobs.filter((job) => job.id !== currentJobId));
		}
	}, [job, jobsState.data.jobs, removeJobStatus.data, removeJobStatus.success, setJobsState]);

	useEffect(() => {
		if (downloadJobStatus.success) {
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
	}, [downloadJobStatus.data, downloadJobStatus.response, downloadJobStatus.success]);

	return useMemo(() => {
		if (!job) {
			return null;
		}
		return (
			<Card fluid>
				<Image fluid src={job.artworkUrl || BlankImage} />
				<Card.Content>
					<Card.Description textAlign="left">
						<List>
							<List.Item>
								<List.Header>ID</List.Header>
								{job.id}
							</List.Item>
							<List.Item>
								<List.Header>Source</List.Header>
								{job.filename || job.youtubeUrl}
							</List.Item>
						</List>
					</Card.Description>
				</Card.Content>
				<Card.Content>
					<Card.Description textAlign="center">
						<List horizontal>
							<List.Item>
								<List.Header>Title</List.Header>
								{job.title}
							</List.Item>
							<List.Item>
								<List.Header>Artist</List.Header>
								{job.artist}
							</List.Item>
							<List.Item>
								<List.Header>Album</List.Header>
								{job.album}
							</List.Item>
							<List.Item>
								<List.Header>Grouping</List.Header>
								{job.grouping}
							</List.Item>
						</List>
					</Card.Description>
				</Card.Content>
				<Card.Content extra>
					<Container>
						<Grid container stackable>
							<Grid.Row columns="equal">
								<Grid.Column>
									{!job.failed ? (
										<Button
											fluid
											loading={!job.completed}
											icon="cloud download"
											color="green"
											onClick={() => downloadJob({ url: `/music/jobs/download/${job.id}`, responseType: 'blob' })}
										/>
									) : null}
									{job.failed ? <Button fluid icon="x" color="red" /> : null}
								</Grid.Column>
								<Grid.Column>
									<Button icon="copy" fluid onClick={() => copyJob()} />
								</Grid.Column>
								<Grid.Column>
									<Button
										icon="trash"
										color="red"
										fluid
										onClick={() => removeJob({ url: `/music/jobs/delete/${job.id}`, method: 'DELETE' })}
									/>
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</Container>
				</Card.Content>
			</Card>
		);
	}, [copyJob, downloadJob, job, removeJob]);
};

export default JobCard;
