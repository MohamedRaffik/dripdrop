import { api } from "./generated/cookiesApi";
import { Tags } from "./tags";

import { transformErrorResponse } from "./utils";

const enhancedApi = api.enhanceEndpoints({
  addTagTypes: [Tags.COOKIES],
  endpoints: {
    getCookiesApiCookiesGet: {
      providesTags: [Tags.COOKIES],
    },
    updateCookiesApiCookiesPost: {
      invalidatesTags: [Tags.COOKIES],
      transformErrorResponse,
    },
    deleteCookiesApiCookiesDelete: {
      invalidatesTags: [Tags.COOKIES],
    },
  },
});

export default enhancedApi;
export const {
  useGetCookiesApiCookiesGetQuery: useCookiesQuery,
  useUpdateCookiesApiCookiesPostMutation: useUpdateCookiesMutation,
  useDeleteCookiesApiCookiesDeleteMutation: useDeleteCookiesMutation,
} = enhancedApi;
