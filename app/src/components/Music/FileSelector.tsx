import React, { useCallback, useEffect, useMemo } from 'react';
import { Button, Switch, TextField } from '@mui/material';
import {
	albumSelector,
	artistSelector,
	artworkURLSelector,
	filenameSelector,
	fileTypeSelector,
	groupingSelector,
	titleSelector,
} from '../../atoms/Music';
import { FILE_TYPE } from '../../utils/enums';
import { defaultTextFieldProps, resolveAlbumFromTitle } from '../../utils/helpers';
import YoutubeURLInput from './YoutubeURLInput';
import useLazyFetch from '../../hooks/useLazyFetch';
import { useRecoilState, useSetRecoilState } from 'recoil';

interface FileSwitchProps {
	fileInputRef: React.MutableRefObject<null | HTMLInputElement>;
}

const FileSwitch = (props: FileSwitchProps) => {
	const { fileInputRef } = props;

	const [filename, setFilename] = useRecoilState(filenameSelector);
	const [fileType, setFileType] = useRecoilState(fileTypeSelector);
	const setTitle = useSetRecoilState(titleSelector);
	const setArtist = useSetRecoilState(artistSelector);
	const setAlbum = useSetRecoilState(albumSelector);
	const setGrouping = useSetRecoilState(groupingSelector);
	const setArtworkURL = useSetRecoilState(artworkURLSelector);

	const [getFileTags, getFileTagsStatus] = useLazyFetch();

	const onFileSwitchChange = useCallback(
		(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
			setFileType(checked ? FILE_TYPE.WAV_UPLOAD : FILE_TYPE.YOUTUBE);
		},
		[setFileType]
	);

	const onBrowseClick = useCallback(() => {
		if (fileType !== FILE_TYPE.YOUTUBE) {
			if (fileInputRef.current) {
				fileInputRef.current.click();
			}
		}
	}, [fileInputRef, fileType]);

	const onFileChange = useCallback(
		async (event: React.ChangeEvent<HTMLInputElement>) => {
			const files = event.target.files;
			if (files && files.length > 0) {
				const file = files[0];
				const formData = new FormData();
				formData.append('file', file);
				setFilename(file.name);
				getFileTags('/music/getTags', { method: 'POST', body: formData });
			}
		},
		[getFileTags, setFilename]
	);

	useEffect(() => {
		if (getFileTagsStatus.isSuccess) {
			const { title, artist, album, grouping, artwork_url } = getFileTagsStatus.data;
			setTitle(title || '');
			setArtist(artist || '');
			setAlbum(album || resolveAlbumFromTitle(title) || '');
			setGrouping(grouping || '');
			setArtworkURL(artwork_url || '');
		}
	}, [getFileTagsStatus.data, getFileTagsStatus.isSuccess, setAlbum, setArtist, setArtworkURL, setGrouping, setTitle]);

	return useMemo(
		() => (
			<React.Fragment>
				<YoutubeURLInput />
				<Switch
					onChange={onFileSwitchChange}
					value={fileType !== FILE_TYPE.YOUTUBE}
					checked={fileType !== FILE_TYPE.YOUTUBE}
				/>
				<TextField
					{...defaultTextFieldProps}
					onClick={onBrowseClick}
					value={filename}
					label="File Upload"
					disabled
					required
					error={filename === '' && fileType !== FILE_TYPE.YOUTUBE}
				/>
				<input ref={fileInputRef} onChange={onFileChange} style={{ display: 'none' }} type="file" accept=".mp3,.wav" />
				<Button
					variant="contained"
					disabled={fileType !== FILE_TYPE.MP3_UPLOAD && fileType !== FILE_TYPE.WAV_UPLOAD}
					onClick={onBrowseClick}
				>
					Browse
				</Button>
			</React.Fragment>
		),
		[fileInputRef, fileType, filename, onBrowseClick, onFileChange, onFileSwitchChange]
	);
};

export default FileSwitch;
