#!/usr/bin/env python
# Before running the script, place your Spotify app key in the current directory.
# You can apply for and download your app key binary from developer.spotify.com.

import getpass
import optparse
import spotify
import spotify.manager

class SpotifySession(spotify.manager.SpotifySessionManager):
    def __init__(self, *args, **kwargs):
        spotify.manager.SpotifySessionManager.__init__(self, *args, **kwargs)
        self.playlist_container = None

    def logged_in(self, session, error):
        if error is None:
            print "Logged in"
        else:
            print "Login error", error
        self.playlist_container = PlaylistContainer(session)

    def logged_out(self, session):
        print "Logged out"

    def metadata_updated(self, session):
        #print "metadata_updated"
        pass

    def connection_error(self, session, msg):
        print "connection_error", msg

    def message_to_user(self, session, msg):
        print "message_to_user", msg

    def play_token_lost(self, session):
        print "play_token_lost"

    def log_message(self, session, msg):
        #print "log_message", msg
        pass

class PlaylistContainer(spotify.manager.SpotifyContainerManager):
    class Folder:
        def __init__(self, name):
            self.name = name
            self.playlists = []
            self.subfolders = []

    def __init__(self, session):
        self.session = session
        self.playlist_container = session.playlist_container()
        self.root = PlaylistContainer.Folder("<root>")
        self.pending_playlists = set()

        print "Loading user's playlists...please wait"
        self.watch(self.playlist_container)

    def container_loaded(self, pc, userdata):
        folder_stack = [self.root]
        for i, item in enumerate(self.playlist_container):
            if isinstance(item, spotify.Playlist):
                folder_stack[-1].playlists.append(item)
                if not item.is_loaded():
                    self.pending_playlists.add(i)
                    item.add_playlist_state_changed_callback(self.playlist_state_changed, i)
            else:   # PlaylistFolder
                if item.type() == "folder_start":
                    folder = PlaylistContainer.Folder(item.name())
                    folder_stack.append(folder)
                elif item.type() == "folder_end":
                    folder = folder_stack.pop()
                    folder_stack[-1].subfolders.append(folder)

        if not self.pending_playlists:
            self.all_playlists_loaded()

    def playlist_state_changed(self, playlist, playlist_id):
        if playlist.is_loaded():
            playlist.remove_callback(self.playlist_state_changed, playlist_id)
            self.pending_playlists.discard(playlist_id)
            if not self.pending_playlists:
                self.all_playlists_loaded()

    def all_playlists_loaded(self):
        def print_folder(folder, level, idx):
            indent = "  " * level
            print "    " + indent + "+ " + folder.name
            for subfolder in folder.subfolders:
                idx = print_folder(subfolder, level + 1, idx)
            for playlist in folder.playlists:
                print "%3i." % idx + indent + "  | " + playlist.name() + " - %d tracks" % len(playlist)
                all_playlists.append(playlist)
                idx += 1
            return idx

        all_playlists = []
        print_folder(self.root, 0, 1)

        playlist_num = int(raw_input("Type playlist number 1..%d: " % len(all_playlists)))
        playlist = all_playlists[playlist_num - 1]
        print "Tracks:"
        for i, track in enumerate(playlist):
            print "%d." % (i + 1), track.name(), "-", track.artists()[0].name()

        self.session.logout()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-u", "--username",
                      help="Spotify username or email (if omitted, relogin the last user)")
    parser.add_option("-p", "--password",
                      help="Passowrd (will be prompted if empty)")
    opts, args = parser.parse_args()
    if opts.username and not opts.password:
        opts.password = getpass.getpass()

    sess = SpotifySession(username=opts.username, password=opts.password, remember_me=True)
    try:
        sess.connect()
    except spotify.SpotifyError, e:
        if not opts.username and not opts.password:
            parser.error("Login failed and no username and password given.")
        else:
            raise
