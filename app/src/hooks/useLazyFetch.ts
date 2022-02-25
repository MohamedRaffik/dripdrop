import { useRef, useCallback, useEffect, useMemo, useReducer } from 'react';
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { apiValidatorErrorParser } from '../utils/helpers';

type LazyFetchState<T> =
	| {
			error: null;
			response: AxiosResponse<T>;
			data: T;
			loading: false;
			success: true;
			timestamp: Date;
	  }
	| {
			error: string;
			response: null;
			data: null;
			loading: false;
			success: false;
			timestamp: Date;
	  }
	| {
			error: null;
			response: null;
			data: null;
			loading: true;
			success: false;
			timestamp: Date;
	  }
	| {
			error: null;
			response: null;
			data: null;
			loading: false;
			success: false;
			timestamp: Date;
	  };

type LazyFetchFn = (config: AxiosRequestConfig) => Promise<void>;

type LazyFetch<T> = [LazyFetchFn, LazyFetchState<T>];

type AsyncAction<T> =
	| {
			type: `LOADING`;
	  }
	| {
			type: `ERROR`;
			payload: { error: string };
	  }
	| {
			type: `SUCCESS`;
			payload: { response: AxiosResponse<T>; data: T };
	  };

const reducer = <T>(state: LazyFetchState<T>, action: AsyncAction<T>): LazyFetchState<T> => {
	if (action.type === 'LOADING') {
		return {
			error: null,
			response: null,
			data: null,
			loading: true,
			success: false,
			timestamp: new Date(Date.now()),
		};
	} else if (action.type === 'ERROR') {
		return {
			error: action.payload.error,
			response: null,
			data: null,
			loading: false,
			success: false,
			timestamp: new Date(Date.now()),
		};
	} else if (action.type === 'SUCCESS') {
		return {
			error: null,
			response: action.payload.response,
			data: action.payload.data,
			loading: false,
			success: true,
			timestamp: new Date(Date.now()),
		};
	}
	return state;
};

const useLazyFetch = <T>(): LazyFetch<T> => {
	const [fetchState, dispatch] = useReducer(reducer, {
		error: null,
		response: null,
		data: null,
		loading: false,
		success: false,
		timestamp: new Date(Date.now()),
	});
	const controller = useRef(new AbortController());

	const triggerFetch: LazyFetchFn = useCallback(async (config: AxiosRequestConfig) => {
		try {
			dispatch({ type: 'LOADING' });
			const response: AxiosResponse<any> = await axios({ ...config, signal: controller.current.signal });
			return dispatch({ type: 'SUCCESS', payload: { response, data: response.data } });
		} catch (error) {
			const { response, request } = error as AxiosError;
			let errorMsg = 'Failed';
			if (response) {
				if (response.data && response.data.detail) {
					errorMsg = response.status === 422 ? apiValidatorErrorParser(response.data.detail) : response.data.detail;
				}
				dispatch({
					type: 'ERROR',
					payload: {
						error: errorMsg,
					},
				});
			} else if (request) {
				dispatch({ type: 'ERROR', payload: { error: 'No response' } });
			} else {
				dispatch({ type: 'ERROR', payload: { error: errorMsg } });
			}
		}
	}, []);

	useEffect(() => {
		let c = controller.current;
		return () => {
			c.abort();
		};
	}, []);

	return useMemo(() => [triggerFetch, fetchState as LazyFetchState<T>], [fetchState, triggerFetch]);
};

export default useLazyFetch;
