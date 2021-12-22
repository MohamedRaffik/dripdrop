import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useRecoilState } from 'recoil';
import { Alert, Button, CircularProgress, Snackbar } from '@mui/material';
import { FILE_TYPE } from '../../utils/enums';
import { initialFormState, musicFormAtom } from '../../atoms/Music';
import BlankImage from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

interface FormActionProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FormActions = (props: FormActionProps) => {
	const { fileInputRef } = props;

	const [openSuccess, setOpenSuccess] = useState(false);
	const [openError, setOpenError] = useState(false);
	const [musicForm, setMusicForm] = useRecoilState(musicFormAtom);

	const { title, artist, album, grouping, artwork_url, filename, fileType, youtube_url } = musicForm;

	const resetForm = useCallback(() => {
		setMusicForm(initialFormState);
	}, [setMusicForm]);

	const [validForm, setValidForm] = useState(false);

	const [performOperation, performOperationStatus] = useLazyFetch();

	const run = useCallback(async () => {
		const formData = new FormData();
		if (
			fileType !== FILE_TYPE.YOUTUBE &&
			fileInputRef.current &&
			fileInputRef.current.files &&
			fileInputRef.current.files.length > 0
		) {
			const file = fileInputRef.current.files[0];
			formData.append('file', file);
		}
		if (fileType === FILE_TYPE.YOUTUBE) {
			formData.append('youtube_url', youtube_url || '');
		}
		if (artwork_url) {
			formData.append('artwork_url', artwork_url);
		} else {
			const imageResponse = await fetch(BlankImage);
			if (imageResponse.ok) {
				const blob = await imageResponse.blob();
				try {
					const readFilePromise = () =>
						new Promise((resolve, reject) => {
							const reader = new FileReader();
							reader.onloadend = () => resolve(reader.result);
							reader.onerror = reject;
							reader.readAsDataURL(blob);
						});
					const url = (await readFilePromise()) as string;
					formData.append('artwork_url', url);
				} catch {}
			}
		}
		formData.append('title', title);
		formData.append('artist', artist);
		formData.append('album', album);
		formData.append('grouping', grouping || '');
		performOperation('/music/download', { method: 'POST', body: formData });
	}, [album, artist, artwork_url, fileInputRef, fileType, grouping, performOperation, title, youtube_url]);

	useEffect(() => {
		if (performOperationStatus.isSuccess) {
			resetForm();
		} else if (performOperationStatus.isError) {
			setOpenError(true);
		}
	}, [performOperationStatus.isError, performOperationStatus.isSuccess, resetForm]);

	useEffect(() => {
		if (
			(fileType === FILE_TYPE.YOUTUBE &&
				youtube_url &&
				RegExp(/^https:\/\/(www\.)?youtube\.com\/watch\?v=.+/).test(youtube_url)) ||
			(fileType !== FILE_TYPE.YOUTUBE && filename)
		) {
			setValidForm(!!title && !!artist && !!album);
		} else {
			setValidForm(false);
		}
	}, [album, artist, fileType, filename, title, youtube_url]);

	return useMemo(
		() => (
			<React.Fragment>
				<Snackbar
					open={openSuccess}
					autoHideDuration={5000}
					anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
					onClose={() => setOpenSuccess(false)}
				>
					<Alert severity="success">Task started successfully.</Alert>
				</Snackbar>
				<Snackbar
					open={openError}
					autoHideDuration={5000}
					anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
					onClose={() => setOpenError(false)}
				>
					<Alert severity="error">Task failed to start.</Alert>
				</Snackbar>
				{!performOperationStatus.isLoading ? (
					<React.Fragment>
						<Button variant="contained" disabled={!validForm} onClick={run}>
							{fileType === FILE_TYPE.YOUTUBE ? 'Download and Set Tags' : ''}
							{fileType === FILE_TYPE.MP3_UPLOAD ? 'Update Tags' : ''}
							{fileType === FILE_TYPE.WAV_UPLOAD ? 'Convert and Update Tags' : ''}
						</Button>
						<Button variant="contained" onClick={resetForm}>
							Reset
						</Button>
					</React.Fragment>
				) : (
					<CircularProgress />
				)}
			</React.Fragment>
		),
		[fileType, openError, openSuccess, performOperationStatus.isLoading, resetForm, run, validForm]
	);
};

export default FormActions;