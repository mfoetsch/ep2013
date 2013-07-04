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

    def logged_in(self, session, error):
        if error is None:
            print "Logged in"
        else:
            print "Login error", error
        self.query = raw_input("Search query: ")
        if not self.query:
            self.query = "ABBA"
        self.result_page = 0
        self.search(self.query, self.result_page)

    def search(self, query, page=0):
        self.session.search(query, self.search_results_loaded,
                            track_offset=page * 5, track_count=5,
                            album_offset=page * 5, album_count=5,
                            artist_offset=page * 5, artist_count=5)
        print "searching...please wait"

    def search_results_loaded(self, results, userdata):
        if len(results.albums()) == len(results.artists()) == len(results.tracks()) == 0:
            print "No more results"
            self.disconnect()
            return
        if results.did_you_mean():
            print 'Did you mean "%s"?' % results.did_you_mean()
            print
        print 'Results for "%s"' % self.query
        print "Total", results.total_albums(), "albums,", results.total_artists(), "artists,",
        print results.total_tracks(), "tracks"
        print
        print "Page", self.result_page + 1
        print
        result_idx = self.result_page * 5 + 1
        if len(results.albums()):
            print "Albums %d-%d" % (result_idx, result_idx + len(results.albums()) - 1)
            print "-" * 30
            for album in results.albums():
                print album.name()
        else:
            print "No more albums"
        print

        if len(results.artists()):
            print "Artists %d-%d" % (result_idx, result_idx + len(results.artists()) - 1)
            print "-" * 30
            for artist in results.artists():
                print artist.name()
        else:
            print "No more artists"
        print

        if len(results.tracks()):
            print "Tracks %d-%d" % (result_idx, result_idx + len(results.tracks()) - 1)
            print "-" * 30
            for track in results.tracks():
                print track.name(), "-", track.artists()[0].name()
        else:
            print "No more tracks"
        print

        try:
            raw_input("Press RETURN")
        except:
            print
            print "Logging out..."
            self.disconnect()
            return
        self.result_page += 1
        self.search(self.query, self.result_page)

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
