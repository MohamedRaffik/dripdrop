import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getYtdlpCookiesApiYtdlpCookiesGet: build.query<
      GetYtdlpCookiesApiYtdlpCookiesGetApiResponse,
      GetYtdlpCookiesApiYtdlpCookiesGetApiArg
    >({
      query: () => ({ url: `/api/ytdlp-cookies` }),
    }),
    updateYtdlpCookiesApiYtdlpCookiesPost: build.mutation<
      UpdateYtdlpCookiesApiYtdlpCookiesPostApiResponse,
      UpdateYtdlpCookiesApiYtdlpCookiesPostApiArg
    >({
      query: (queryArg) => ({
        url: `/api/ytdlp-cookies`,
        method: "POST",
        body: queryArg,
      }),
    }),
    deleteYtdlpCookiesApiYtdlpCookiesDelete: build.mutation<
      DeleteYtdlpCookiesApiYtdlpCookiesDeleteApiResponse,
      DeleteYtdlpCookiesApiYtdlpCookiesDeleteApiArg
    >({
      query: () => ({ url: `/api/ytdlp-cookies`, method: "DELETE" }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetYtdlpCookiesApiYtdlpCookiesGetApiResponse = /** status 200 Successful Response */ YtdlpCookiesResponse;
export type GetYtdlpCookiesApiYtdlpCookiesGetApiArg = void;
export type UpdateYtdlpCookiesApiYtdlpCookiesPostApiResponse =
  /** status 200 Successful Response */ YtdlpCookiesResponse;
export type UpdateYtdlpCookiesApiYtdlpCookiesPostApiArg = UpdateYtdlpCookies;
export type DeleteYtdlpCookiesApiYtdlpCookiesDeleteApiResponse = unknown;
export type DeleteYtdlpCookiesApiYtdlpCookiesDeleteApiArg = void;
export type YtdlpCookiesResponse = {
  cookies: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type UpdateYtdlpCookies = {
  cookies: string;
};
export const {
  useGetYtdlpCookiesApiYtdlpCookiesGetQuery,
  useLazyGetYtdlpCookiesApiYtdlpCookiesGetQuery,
  useUpdateYtdlpCookiesApiYtdlpCookiesPostMutation,
  useDeleteYtdlpCookiesApiYtdlpCookiesDeleteMutation,
} = injectedRtkApi;
