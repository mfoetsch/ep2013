#!/usr/bin/env python
# When running the script, set environment variables ECHO_NEST_API_KEY,
# ECHO_NEST_CONSUMER_KEY, ECHO_NEST_SHARED_SECRET. They will be used
# by pyechonest.config.

import optparse
import time
from pyechonest import catalog, playlist, track

TRACKS = ["spotify-WW:track:5xtwX31B89apd0farwIgir",
          "spotify-WW:track:4OLlcgkQR9V9Eqk8sUEjtY",
          "spotify-WW:track:6XIWqXj7Tps4dAJ1wSO8Qe",
          "spotify-WW:track:23bLv4aPf9Nt53KCybyFKf",
          "spotify-WW:track:60rHc4AkLlP4XVSATvBb6K"]
CATALOG_NAME = "Spotify Hackweek"

def update_catalog(cat):
    print "Updating catalog..."
    update_items = []
    for i, uri in enumerate(TRACKS):
        print "Track", i, "of", len(TRACKS)
        t = track.track_from_id(uri)
        update_items.append({"action": "update",
                             "item": {"item_id": uri.split(":")[-1],
                                        # item_id can be anything as long as it's unique
                                      "song_id": t.song_id}})
                                        # song_id is the Echo Nest ID of the Spotify track
    ticket = cat.update(update_items)
    while True:
        status = cat.status(ticket)["ticket_status"]
        print "Catalog update status:", status
        if status != "pending":
            break
        time.sleep(1)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-c", "--catalog-id",
                      help="ID of an existing Echo Nest catalog")
    parser.add_option("-n", "--catalog-name", default="Spotify Hackweek",
                      help="Name of existing or new Echo Nest catalog")
    opts, args = parser.parse_args()

    if opts.catalog_id:
        # Use an existing catalog.
        cat = catalog.Catalog(opts.catalog_id)
    else:
        # Use an existing catalog or create a new one.
        cat = catalog.Catalog(opts.catalog_name, "song")

    cat_items = cat.get_item_dicts()
    if cat_items:
        # Catalog already contains items.
        print len(cat_items), "items in catalog"
    else:
        # Catalog is empty. Add some items.
        update_catalog(cat)

    print "Creating playlist based on tracks in catalog..."
    pl = playlist.static(type="catalog-radio", seed_catalog=cat,
                         buckets=["id:spotify-WW", "tracks"])
    for i, s in enumerate(pl):
        print "%2d. %s by %s" % (i + 1, s.title, s.artist_name)
        for t in s.get_tracks("spotify-WW"):
            print " ", t["foreign_id"].replace("spotify-WW", "spotify")
            break   # print only the first Spotify track URI
