#!/usr/bin/env python
# Before running the script, place your Spotify app key in the current directory.
# You can apply for and download your app key binary from developer.spotify.com.

import getpass
import optparse
import spotify
import spotify.manager
import time
from spotify.audiosink import import_audio_sink

AudioSink = import_audio_sink()

class SpotifySession(spotify.manager.SpotifySessionManager):
    def __init__(self, *args, **kwargs):
        spotify.manager.SpotifySessionManager.__init__(self, *args, **kwargs)
        self.audio = AudioSink(backend=self)

    def logged_in(self, session, error):
        if error is None:
            print "Logged in"
        else:
            print "Login error", error
        query = raw_input("Search query: ")
        if not query:
            query = "ABBA"
        self.session.search(query, self.search_results_loaded, track_count=5,
                            album_count=0, artist_count=0, playlist_count=0)
        print "loading search results...please wait"

    def search_results_loaded(self, results, userdata):
        if len(results.tracks()) == 0:
            print "No tracks to play"
            self.disconnect()
            return
        self.upcoming_tracks = list(results.tracks())
        self.track_idx = 0
        self.load_track(self.upcoming_tracks[self.track_idx])

    def load_track(self, track):
        print "Loading track..."
        while not track.is_loaded():
            time.sleep(0.1)
        if track.is_autolinked():
            # For example, the album this track is on is not available in
            # your country, but the same track is on another album that is
            # available. Redirect to that version of the track instead.
            # This shouldn't happen when we're receiving search results, but it
            # can happen, for example, if you resolve a spotify:track:... URI.
            track = self.load_track(track.playable())
        if track.availability() != 1:
            print "Track not available (%s)" % track.availability()
        print "Playing track", self.track_idx + 1, "of", len(self.upcoming_tracks)
        print track.name(), "by", track.artists()[0].name()
        self.session.load(track)
        self.audio.start()
        self.session.play(1)

    def music_delivery_safe(self, session, frames, frame_size, num_frames,
                            sample_type, sample_rate, channels):
        return self.audio.music_delivery(session, frames, frame_size, num_frames,
                                         sample_type, sample_rate, channels)

    def end_of_track(self, session):
        print "End of track"
        self.track_idx += 1
        if self.track_idx < self.upcoming_tracks:
            self.load_track(self.upcoming_tracks[self.track_idx])
        else:
            print "Last track played. Logging out."
            self.disconnect()

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
