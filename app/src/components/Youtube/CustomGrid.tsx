import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { Box, Fab, Grid, Skeleton } from '@mui/material';
import { ArrowUpward } from '@mui/icons-material';
import ConditionalDisplay from '../ConditionalDisplay';

interface CustomGridProps<T> {
	items: T[];
	itemKey: (item: T) => any;
	renderItem: (item: T) => JSX.Element;
	perPage: number;
	isFetching?: boolean;
	fetchMore?: () => void;
	layout: {
		md?: number;
		sm?: number;
		xs?: number;
	};
}

const CustomGrid = <T,>(props: CustomGridProps<T>) => {
	const { items, renderItem, isFetching, perPage, fetchMore, itemKey, layout } = props;
	const [showScrollButton, setShowScrollButton] = useState(false);

	const gridRef = useRef<HTMLDivElement | null>(null);

	const itemsToRender = useMemo(() => {
		const elements = items.map((item) => (
			<Grid key={`grid-${itemKey(item)}`} item {...layout} padding={1}>
				{renderItem(item)}
			</Grid>
		));

		if (isFetching) {
			elements.push(
				...Array(perPage)
					.fill(0)
					.map((v, i) => (
						<Grid key={`grid-${i}`} item {...layout} padding={1}>
							<Skeleton sx={{ height: elements.length > 0 ? '100%' : '30vh' }} variant="rectangular" />
						</Grid>
					))
			);
		}
		return elements;
	}, [items, isFetching, itemKey, layout, renderItem, perPage]);

	const onGridBottom = useCallback(() => {
		if (document.body.offsetHeight - 500 < window.innerHeight + window.scrollY) {
			if (!isFetching && fetchMore) {
				fetchMore();
			}
		}
	}, [fetchMore, isFetching]);

	const updateScrollButton = useCallback(() => {
		if (gridRef.current) {
			const grid = gridRef.current;
			const gridCoordinates = grid.getBoundingClientRect();
			if (gridCoordinates.y < 0 && !showScrollButton) {
				setShowScrollButton(true);
			} else if (gridCoordinates.y > 0 && showScrollButton) {
				setShowScrollButton(false);
			}
		}
	}, [showScrollButton]);

	useEffect(() => {
		window.addEventListener('scroll', updateScrollButton);
		window.addEventListener('scroll', onGridBottom);
		return () => {
			window.removeEventListener('scroll', onGridBottom);
			window.removeEventListener('scroll', updateScrollButton);
		};
	}, [onGridBottom, updateScrollButton]);

	return (
		<Box>
			<Grid ref={gridRef} container>
				{itemsToRender}
			</Grid>
			<ConditionalDisplay condition={showScrollButton}>
				<Box
					sx={{
						position: 'fixed',
						right: '5vw',
						bottom: '10vh',
					}}
				>
					<Fab
						variant="circular"
						color="primary"
						onClick={() => {
							if (gridRef.current) {
								window.scrollTo({ top: gridRef.current.offsetTop - 100, behavior: 'smooth' });
							}
						}}
					>
						<ArrowUpward />
					</Fab>
				</Box>
			</ConditionalDisplay>
		</Box>
	);
};

export default CustomGrid;
