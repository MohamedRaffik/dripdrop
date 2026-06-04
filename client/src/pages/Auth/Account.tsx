import { Button, Checkbox, Container, Group, Modal, PasswordInput, Stack, Tabs, Textarea, TextInput } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";

import { useCheckSessionQuery, useLogoutMutation } from "../../api/auth";
import { useWebdavQuery, useUpdateWebdavMutation, useDeleteWebdavMutation } from "../../api/webdav";
import {
  useYtdlpCookiesQuery,
  useUpdateYtdlpCookiesMutation,
  useDeleteYtdlpCookiesMutation,
} from "../../api/ytdlpCookies";

const AccountTabs = {
  ACCOUNT: "account",
  WEBDAV: "webdav",
  YTDLP_COOKIES: "ytdlp-cookies",
  LEGAL: "legal",
} as const;

const Account = () => {
  const sessionStatus = useCheckSessionQuery();
  const [logout, logoutStatus] = useLogoutMutation();
  const webdavStatus = useWebdavQuery();
  const [updateWebDav, updateWebDavStatus] = useUpdateWebdavMutation();
  const [deleteWebDav, deleteWebDavStatus] = useDeleteWebdavMutation();
  const ytdlpCookiesStatus = useYtdlpCookiesQuery();
  const [updateYtdlpCookies, updateYtdlpCookiesStatus] = useUpdateYtdlpCookiesMutation();
  const [deleteYtdlpCookies, deleteYtdlpCookiesStatus] = useDeleteYtdlpCookiesMutation();

  const [webdavInfo, setWebdavInfo] = useState({ username: "", password: "", url: "" });
  const [ytdlpCookiesInfo, setYtdlpCookiesInfo] = useState({ cookies: "" });
  const [webdavDeleteOpened, webdavDeleteHandlers] = useDisclosure(false);
  const [ytdlpCookiesDeleteOpened, ytdlpCookiesDeleteHandlers] = useDisclosure(false);

  const user = useMemo(() => {
    if (sessionStatus.isSuccess && sessionStatus.currentData) {
      return sessionStatus.currentData;
    }
    return null;
  }, [sessionStatus.currentData, sessionStatus.isSuccess]);

  useEffect(() => {
    if (webdavStatus.isSuccess && webdavStatus.currentData) {
      setWebdavInfo(webdavStatus.currentData);
    } else {
      setWebdavInfo({ username: "", password: "", url: "" });
    }
  }, [webdavStatus.currentData, webdavStatus.isSuccess]);

  useEffect(() => {
    if (ytdlpCookiesStatus.isSuccess && ytdlpCookiesStatus.currentData) {
      setYtdlpCookiesInfo(ytdlpCookiesStatus.currentData);
    } else {
      setYtdlpCookiesInfo({ cookies: "" });
    }
  }, [ytdlpCookiesStatus.currentData, ytdlpCookiesStatus.isSuccess]);

  if (user) {
    return (
      <Container>
        <Helmet>
          <title>Account</title>
        </Helmet>
        <Tabs defaultValue={AccountTabs.ACCOUNT}>
          <Tabs.List>
            <Tabs.Tab value={AccountTabs.ACCOUNT}>Account</Tabs.Tab>
            <Tabs.Tab value={AccountTabs.WEBDAV}>WebDAV</Tabs.Tab>
            <Tabs.Tab value={AccountTabs.YTDLP_COOKIES}>yt-dlp Cookies</Tabs.Tab>
            <Tabs.Tab value={AccountTabs.LEGAL}>Legal</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value={AccountTabs.ACCOUNT}>
            <Stack p="md">
              <TextInput label="Email" value={user.email} readOnly />
              <Checkbox label="Admin" checked={user.admin} readOnly />
              <Button variant="light" color="red" onClick={() => logout()} loading={logoutStatus.isLoading}>
                Logout
              </Button>
            </Stack>
          </Tabs.Panel>
          <Tabs.Panel value={AccountTabs.WEBDAV}>
            <Stack p="md">
              <TextInput
                label="Username"
                value={webdavInfo.username}
                onChange={(e) => setWebdavInfo({ ...webdavInfo, username: e.target.value })}
                withAsterisk
              />
              <PasswordInput
                label="Password"
                value={webdavInfo.password}
                onChange={(e) => setWebdavInfo({ ...webdavInfo, password: e.target.value })}
                withAsterisk
              />
              <TextInput
                label="URL"
                value={webdavInfo.url}
                onChange={(e) => setWebdavInfo({ ...webdavInfo, url: e.target.value })}
                withAsterisk
              />
              {updateWebDavStatus.isError && <p style={{ color: "red" }}>{String(updateWebDavStatus.error)}</p>}
              {updateWebDavStatus.isSuccess && <p style={{ color: "green" }}>WebDAV Updated</p>}
              <Group justify="flex-end" grow>
                <Button color="red" onClick={webdavDeleteHandlers.open} loading={deleteWebDavStatus.isLoading}>
                  Delete
                </Button>
                <Button onClick={() => updateWebDav(webdavInfo)} loading={updateWebDavStatus.isLoading}>
                  Save
                </Button>
              </Group>
            </Stack>
            <Modal opened={webdavDeleteOpened} onClose={webdavDeleteHandlers.close} title="Confirm Delete" centered>
              <Stack p="md">
                <p>Are you sure you want to delete your WebDAV account?</p>
                <Group justify="flex-end" grow>
                  <Button color="red" onClick={webdavDeleteHandlers.close}>
                    Cancel
                  </Button>
                  <Button onClick={() => deleteWebDav().then(webdavDeleteHandlers.close)} loading={deleteWebDavStatus.isLoading}>
                    Delete
                  </Button>
                </Group>
              </Stack>
            </Modal>
          </Tabs.Panel>
          <Tabs.Panel value={AccountTabs.YTDLP_COOKIES}>
            <Stack p="md">
              <Textarea
                label="Cookies"
                description="Paste the contents of a Netscape-format cookies.txt file. These are used when downloading audio with yt-dlp."
                value={ytdlpCookiesInfo.cookies}
                onChange={(e) => setYtdlpCookiesInfo({ cookies: e.target.value })}
                minRows={10}
                autosize
                withAsterisk
                styles={{ input: { fontFamily: "monospace" } }}
              />
              {updateYtdlpCookiesStatus.isError && (
                <p style={{ color: "red" }}>{String(updateYtdlpCookiesStatus.error)}</p>
              )}
              {updateYtdlpCookiesStatus.isSuccess && <p style={{ color: "green" }}>Cookies Updated</p>}
              <Group justify="flex-end" grow>
                <Button
                  color="red"
                  onClick={ytdlpCookiesDeleteHandlers.open}
                  loading={deleteYtdlpCookiesStatus.isLoading}
                >
                  Delete
                </Button>
                <Button
                  onClick={() => updateYtdlpCookies(ytdlpCookiesInfo)}
                  loading={updateYtdlpCookiesStatus.isLoading}
                >
                  Save
                </Button>
              </Group>
            </Stack>
            <Modal
              opened={ytdlpCookiesDeleteOpened}
              onClose={ytdlpCookiesDeleteHandlers.close}
              title="Confirm Delete"
              centered
            >
              <Stack p="md">
                <p>Are you sure you want to delete your yt-dlp cookies?</p>
                <Group justify="flex-end" grow>
                  <Button color="red" onClick={ytdlpCookiesDeleteHandlers.close}>
                    Cancel
                  </Button>
                  <Button
                    onClick={() => deleteYtdlpCookies().then(ytdlpCookiesDeleteHandlers.close)}
                    loading={deleteYtdlpCookiesStatus.isLoading}
                  >
                    Delete
                  </Button>
                </Group>
              </Stack>
            </Modal>
          </Tabs.Panel>
          <Tabs.Panel value={AccountTabs.LEGAL}>
            <Stack p="md">
              <Button component={Link} to="/terms">
                Terms of Service
              </Button>
              <Button component={Link} to="/privacy">
                Privacy Policy
              </Button>
            </Stack>
          </Tabs.Panel>
        </Tabs>
      </Container>
    );
  }
  return null;
};

export default Account;
