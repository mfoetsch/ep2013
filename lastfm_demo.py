#!/usr/bin/env python
# Set environment variables LASTFM_API_KEY and LASTFM_SECRET to the
# values for your API account. See http://www.last.fm/api/account. 
# This script uses pyechonest to convert Spotify URIs to Last.fm track IDs.
# When running the script, set environment variables ECHO_NEST_API_KEY,
# ECHO_NEST_CONSUMER_KEY, ECHO_NEST_SHARED_SECRET. They will be used
# by pyechonest.config.

import getpass
import optparse
import os
import pylast
import time
import pyechonest.song
import pyechonest.track

API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_SECRET")

def getLastFmTrackFromSpotifyUri(lastfm_network, spotify_track_uri):
    # Use pyechonest to get the MusicBrainz ID for the Spotify track URI
    # and get the Last.fm track object for the MusicBrainz ID.
    # There may be several MusicBrainz IDs for a single Spotify track,
    # and not all of them can be resolved to Last.fm tracks, so we try
    # all of them. This requires a few network requests. Alternatively,
    # we could create the Last.fm track based on song title and artist name.
    t = pyechonest.track.track_from_id(spotify_track_uri)
    s = pyechonest.song.Song(t.song_id, buckets=["id:musicbrainz", "tracks"])
    for t in s.get_tracks("musicbrainz"):
        foreign_id = t["foreign_id"].replace("musicbrainz:track:", "")
        try:
            lastfm_track = lastfm_network.get_track_by_mbid(foreign_id)
        except pylast.WSError:
            pass
        else:
            return lastfm_track
    else:
        # If the ID mapping fails, try with artist name and song title.
        return pylast.Track(s.artist_name, s.title, lastfm_network)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-u", "--username", help="Last.fm username")
    parser.add_option("-p", "--password",
                      help="Last.fm password (will be prompted if empty)")
    opts, args = parser.parse_args()

    if not opts.username:
        parser.error("Last.fm username must be specified")
    if not opts.password:
        opts.password = getpass.getpass()

    password_hash = pylast.md5(opts.password)
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=opts.username, password_hash=password_hash)

    # Convert Spotify URI to pylast object.
    print "Looking up track on Last.fm..."
    track = getLastFmTrackFromSpotifyUri(network, "spotify-WW:track:2goLsvvODILDzeeiT4dAoR")
    print track

    # Report the "Now Playing" track. This will show up on your Last.fm profile
    # page: http://last.fm/user/<username>
    network.update_now_playing(track.artist.get_name(), track.get_title(), track.get_mbid())

    # Scrobble a track.
    network.scrobble(track.artist.get_name(), track.get_title(), int(time.time() - 30),
                     mbid=track.get_mbid())

    # Love the track.
    track.love()

    print
    print "Similar tracks:"
    for item in track.get_similar()[:10]:
        print item.item

    print
    print "User's artists:"
    user = network.get_authenticated_user()
    library = user.get_library()
    for item in library.get_artists(limit=5):
        print item.item, "(played %d times)" % item.playcount

    print
    score, shared_artists = user.compare_with_user("averagemike")
    print 'Similarity to user "averagemike":', score
    print "Shared artists:", map(str, shared_artists)
