import React, { useEffect } from 'react';
import {
	Stack,
	Typography,
	Select,
	MenuItem,
	Chip,
	Button,
	ToggleButtonGroup,
	ToggleButton,
	Box,
	Pagination,
} from '@mui/material';
import { SetterOrUpdater } from 'recoil';
import useLazyFetch from '../../hooks/useLazyFetch';
import _ from 'lodash';

const FiltersView = (props: {
	children: JSX.Element;
	state: YoutubeVideosViewState;
	updateState: SetterOrUpdater<YoutubeVideosViewState>;
}) => {
	const { state, updateState } = props;
	const [getVideos, getVideosState] = useLazyFetch<YoutubeVideoResponse>();

	useEffect(() => {
		if (getVideosState.isSuccess) {
			const { videos, total_videos } = getVideosState.data;
			updateState((prev) => ({ ...prev, videos, total_videos }));
		}
	}, [getVideosState.data, getVideosState.isSuccess, updateState]);

	const { categories, selectedCategories, per_page, page, total_videos } = state;

	const resolveCategory = (id: number) => {
		if (id === -1) {
			return { id: -1, name: 'All', created_at: '' };
		}
		return categories.find((category: YoutubeVideoCategory) => category.id === id) as YoutubeVideoCategory;
	};

	const updateFilters = (opt: Options) => {
		opt = {
			per_page: opt.per_page ?? per_page,
			page: opt.page ?? page,
			selectedCategories: opt.selectedCategories ?? selectedCategories,
		};
		if (!_.isEqual(opt, { per_page, page, selectedCategories })) {
			const query_categories =
				opt.selectedCategories && opt.selectedCategories.length
					? `?${opt.selectedCategories
							.filter((v) => v !== -1)
							.map((v) => `video_categories=${v}`)
							.join('&')}`
					: '';
			updateState((prev) => ({ ...prev, ...opt }));
			getVideos({ url: `/youtube/videos/${opt.page}/${opt.per_page}${query_categories}` });
		}
	};

	return (
		<React.Fragment>
			<Stack sx={{ my: 2 }} direction="row" alignItems="center" spacing={2}>
				<Typography variant="subtitle1">Categories</Typography>
				<Select
					value={selectedCategories.length === 0 ? [-1] : selectedCategories}
					multiple
					renderValue={(selected) => {
						selected = selected.length === 1 && selected[0] === -1 ? selected : selected.filter((v) => v !== -1);
						return (
							<Stack direction="row" flexWrap="wrap">
								{selected.map((value) => (
									<Chip sx={{ m: 0.5 }} color="primary" key={value} label={resolveCategory(value).name} />
								))}
							</Stack>
						);
					}}
					variant="standard"
					onChange={(e) => {
						let value = typeof e.target.value === 'string' ? [-1] : e.target.value;
						let v = e.target.value;
						if (typeof v === 'string') {
							value = v.split(',').map((v) => Number(v)) as number[];
						}
						updateFilters({ selectedCategories: value });
					}}
				>
					{[...categories]
						.sort((a, b) => (a.name > b.name ? 1 : -1))
						.map((category) => {
							return (
								<MenuItem key={category.id} value={category.id}>
									<Typography>{category.name}</Typography>
								</MenuItem>
							);
						})}
				</Select>
				<Button variant="contained" onClick={() => updateFilters({ selectedCategories: [] })}>
					Reset
				</Button>
				<Box sx={{ flexGrow: 1 }} />
				<ToggleButtonGroup exclusive value={per_page} onChange={(e, v) => updateFilters({ per_page: v })}>
					{([10, 25, 50] as PageState['per_page'][]).map((v) => (
						<ToggleButton key={v} value={v}>
							{v}
						</ToggleButton>
					))}
				</ToggleButtonGroup>
			</Stack>
			{props.children}
			<Stack direction="row" sx={{ my: 5 }} justifyContent="center">
				<Pagination
					page={page}
					onChange={(e, page) => updateFilters({ page })}
					count={Math.ceil(total_videos / per_page)}
					color="primary"
				/>
			</Stack>
		</React.Fragment>
	);
};

export default FiltersView;