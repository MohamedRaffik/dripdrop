import { api } from "./generated/webdavApi";
import { Tags } from "./tags";

import { transformErrorResponse } from "./utils";

const enhancedApi = api.enhanceEndpoints({
  addTagTypes: [Tags.WEBDAV],
  endpoints: {
    getWebdavApiWebdavGet: {
      providesTags: [Tags.WEBDAV],
    },
    updateWebdavApiWebdavPost: {
      invalidatesTags: [Tags.WEBDAV, Tags.USER],
      transformErrorResponse,
    },
    deleteWebdavApiWebdavDelete: {
      invalidatesTags: [Tags.WEBDAV, Tags.USER],
    },
  },
});

export default enhancedApi;
export const {
  useGetWebdavApiWebdavGetQuery: useWebdavQuery,
  useUpdateWebdavApiWebdavPostMutation: useUpdateWebdavMutation,
  useDeleteWebdavApiWebdavDeleteMutation: useDeleteWebdavMutation,
} = enhancedApi;
