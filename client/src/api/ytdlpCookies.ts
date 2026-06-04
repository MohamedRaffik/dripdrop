import { api } from "./generated/ytdlpCookiesApi";
import { Tags } from "./tags";

import { transformErrorResponse } from "./utils";

const enhancedApi = api.enhanceEndpoints({
  addTagTypes: [Tags.YTDLP_COOKIES],
  endpoints: {
    getYtdlpCookiesApiYtdlpCookiesGet: {
      providesTags: [Tags.YTDLP_COOKIES],
    },
    updateYtdlpCookiesApiYtdlpCookiesPost: {
      invalidatesTags: [Tags.YTDLP_COOKIES],
      transformErrorResponse,
    },
    deleteYtdlpCookiesApiYtdlpCookiesDelete: {
      invalidatesTags: [Tags.YTDLP_COOKIES],
    },
  },
});

export default enhancedApi;
export const {
  useGetYtdlpCookiesApiYtdlpCookiesGetQuery: useYtdlpCookiesQuery,
  useUpdateYtdlpCookiesApiYtdlpCookiesPostMutation: useUpdateYtdlpCookiesMutation,
  useDeleteYtdlpCookiesApiYtdlpCookiesDeleteMutation: useDeleteYtdlpCookiesMutation,
} = enhancedApi;
