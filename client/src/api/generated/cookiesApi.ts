import { api } from "./api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getCookiesApiCookiesGet: build.query<GetCookiesApiCookiesGetApiResponse, GetCookiesApiCookiesGetApiArg>({
      query: () => ({ url: `/api/cookies` }),
    }),
    updateCookiesApiCookiesPost: build.mutation<UpdateCookiesApiCookiesPostApiResponse, UpdateCookiesApiCookiesPostApiArg>({
      query: (queryArg) => ({
        url: `/api/cookies`,
        method: "POST",
        body: queryArg,
      }),
    }),
    deleteCookiesApiCookiesDelete: build.mutation<
      DeleteCookiesApiCookiesDeleteApiResponse,
      DeleteCookiesApiCookiesDeleteApiArg
    >({
      query: () => ({ url: `/api/cookies`, method: "DELETE" }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetCookiesApiCookiesGetApiResponse = /** status 200 Successful Response */ CookiesResponse;
export type GetCookiesApiCookiesGetApiArg = void;
export type UpdateCookiesApiCookiesPostApiResponse = /** status 200 Successful Response */ CookiesResponse;
export type UpdateCookiesApiCookiesPostApiArg = UpdateCookies;
export type DeleteCookiesApiCookiesDeleteApiResponse = unknown;
export type DeleteCookiesApiCookiesDeleteApiArg = void;
export type CookiesResponse = {
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
export type UpdateCookies = {
  cookies: string;
};
export const {
  useGetCookiesApiCookiesGetQuery,
  useLazyGetCookiesApiCookiesGetQuery,
  useUpdateCookiesApiCookiesPostMutation,
  useDeleteCookiesApiCookiesDeleteMutation,
} = injectedRtkApi;
