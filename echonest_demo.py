#!/usr/bin/env python
# When running the script, set environment variables ECHO_NEST_API_KEY,
# ECHO_NEST_CONSUMER_KEY, ECHO_NEST_SHARED_SECRET. They will be used
# by pyechonest.config.

from pyechonest import artist
from pyechonest import song

def song_search():
    songs = song.search(min_tempo=120, max_tempo=160, artist_start_year_after=1980,
                        artist_end_year_before=2000, min_danceability=0.6,
                        artist_min_familiarity=0.5, buckets=["id:spotify-WW", "tracks"])
    for s in songs:
        print s.title, "by", s.artist_name
        for t in s.get_tracks("spotify-WW"):
            uri = t["foreign_id"].replace("spotify-WW", "spotify")
            print " ", uri

def artist_bio():
    a = artist.Artist("spotify-WW:artist:0LcJLqbBmaGUft1e9Mm8HV")
    for bio in a.biographies:
        print "-" * 50
        print bio["text"]
        print "-", bio["site"], "<%s>" % bio["url"]
        print
    for review in a.reviews:
        print "-" * 50
        print "Review:", review["name"]
        print review["summary"]
        print "-", review["url"]
        print

def similar_artists():
    artists = [artist.Artist("spotify-WW:artist:2SHhfs4BiDxGQ3oxqf0UHY"),
               artist.Artist("spotify-WW:artist:0LcJLqbBmaGUft1e9Mm8HV")]
    print "Artists similar to", ", ".join([a.name for a in artists])
    for a in artist.similar(ids=[a.id for a in artists], buckets=["id:spotify-WW"]):
        print "-", a.name, "(%s)" % a.get_foreign_id("spotify-WW").replace("spotify-WW", "spotify")

if __name__ == "__main__":
    song_search()
    artist_bio()
    similar_artists()

