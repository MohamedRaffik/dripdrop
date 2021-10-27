import React, { useRef, useContext } from 'react';
import {
	Container,
	Divider,
	Typography,
	TextField,
	Switch,
	Button,
	TextFieldProps,
	Stack,
	CircularProgress,
} from '@mui/material';
import { YouTube } from '@mui/icons-material';
import Image from '../images/blank_image.jpeg';
import { FILE_TYPE } from '../utils/enums';
// import { useDebounce } from '../utils/helpers';
// import Job from '../components/job_card';
import { MusicContext } from '../context/music_context';

const MusicDownloader = () => {
	const { updateFormInputs, formInputs, performOperation, updatingForm, validForm, resetForm } =
		useContext(MusicContext);
	const { fileType, filename, youtubeURL, artworkURL, title, artist, album, grouping } = formInputs;
	// const debouncedYouTubeURL = useDebounce(youTubeURL, 500);
	// const debouncedArtworkURL = useDebounce(artworkURL, 250);

	const fileInputRef: React.MutableRefObject<null | HTMLInputElement> = useRef(null);

	const onFileSwitchChange = (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
		if (checked) {
			updateFormInputs({ fileType: FILE_TYPE.WAV_UPLOAD });
		} else {
			if (fileInputRef.current && fileInputRef.current.files) {
				fileInputRef.current.files = null;
			}
			updateFormInputs({ fileType: FILE_TYPE.YOUTUBE });
		}
	};

	const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const files = event.target.files;
		if (files && files.length > 0) {
			const file = files[0];
			updateFormInputs({ filename: file.name });
		}
	};

	const onBrowseClick = () => {
		if (fileInputRef.current) {
			fileInputRef.current.click();
		}
	};

	const defaultTextFieldProps: TextFieldProps = {
		sx: { mx: 3, flex: 1 },
		variant: 'standard',
	};

	const run = () => {
		if (fileInputRef.current && fileInputRef.current.files && fileInputRef.current.files.length > 0) {
			const file = fileInputRef.current.files[0];
			performOperation(file);
		} else {
			performOperation();
		}
	};

	return (
		<Container>
			<Container>
				<Typography sx={{ my: 5 }} variant="h2">
					MP3 Downloader / Convertor
				</Typography>
				<Divider variant="middle" />
				<Stack direction="row" alignItems="center" sx={{ my: 10 }}>
					<YouTube
						sx={{
							color: fileType === FILE_TYPE.YOUTUBE ? 'red' : 'grey',
						}}
					/>
					<TextField
						{...defaultTextFieldProps}
						required
						value={youtubeURL}
						label="YouTube URL"
						disabled={fileType !== FILE_TYPE.YOUTUBE}
						onChange={(e) => updateFormInputs({ youtubeURL: e.target.value })}
						error={youtubeURL === '' && fileType === FILE_TYPE.YOUTUBE}
						helperText={youtubeURL === '' ? '' : 'Must be a valid YouTube link.'}
					/>
					<Switch onChange={onFileSwitchChange} value={fileType !== FILE_TYPE.YOUTUBE} />
					<TextField
						{...defaultTextFieldProps}
						onClick={onBrowseClick}
						value={filename}
						label="File Upload"
						disabled
						required
						error={filename === '' && fileType !== FILE_TYPE.YOUTUBE}
					/>
					<input
						ref={fileInputRef}
						onChange={onFileChange}
						style={{ display: 'none' }}
						type="file"
						accept=".mp3,.wav"
					/>
					<Button
						variant="contained"
						disabled={fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD}
						onClick={onBrowseClick}
					>
						Browse
					</Button>
				</Stack>
				<Stack direction="row" alignItems="center" sx={{ my: 10 }}>
					<TextField
						{...defaultTextFieldProps}
						label="Artwork URL"
						value={artworkURL}
						onChange={(e) => updateFormInputs({ artworkURL: e.target.value })}
						helperText={'Supports soundcloud links to get cover art'}
					/>
					<img style={{ flex: 1, maxHeight: '40em', maxWidth: '50%' }} src={artworkURL || Image} alt="Cover Art" />
				</Stack>
				<Stack direction="row" alignItems="center" sx={{ my: 10 }}>
					<TextField
						label="Title"
						required
						{...defaultTextFieldProps}
						value={title}
						onChange={(e) => updateFormInputs({ title: e.target.value })}
					/>
					<TextField
						label="Artist"
						required
						{...defaultTextFieldProps}
						value={artist}
						onChange={(e) => updateFormInputs({ artist: e.target.value })}
					/>
					<TextField
						label="Album"
						required
						{...defaultTextFieldProps}
						value={album}
						onChange={(e) => updateFormInputs({ album: e.target.value })}
					/>
					<TextField
						label="Grouping"
						{...defaultTextFieldProps}
						value={grouping}
						onChange={(e) => updateFormInputs({ grouping: e.target.value })}
					/>
				</Stack>
				<Stack direction="row" alignItems="center" justifyContent="center" spacing={2} sx={{ my: 10 }}>
					{updatingForm ? (
						<CircularProgress />
					) : (
						<React.Fragment>
							<Button variant="contained" disabled={!validForm} onClick={run}>
								{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
								{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
								{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
							</Button>
						</React.Fragment>
					)}
					<Button variant="contained" onClick={resetForm}>
						Reset
					</Button>
				</Stack>
			</Container>
		</Container>
	);
};

export default MusicDownloader;
