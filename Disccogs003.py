import discogs_client


def format_artist_names(artists):
    if not artists:
        return 'Unknown artist'
    return ', '.join(getattr(artist, 'name', str(artist)) for artist in artists)


def print_artist_album_table(releases):
    rows = []
    for item in releases:
        release = getattr(item, 'release', None)
        if release is None:
            continue
        artist = format_artist_names(getattr(release, 'artists', []))
        album = getattr(release, 'title', 'Unknown album')
        rows.append((artist, album))

    headers = ['artist', 'album']
    widths = [len(header) for header in headers]
    for row in rows:
        widths[0] = max(widths[0], len(str(row[0])))
        widths[1] = max(widths[1], len(str(row[1])))

    print(' | '.join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print('-+-'.join('-' * width for width in widths))
    for artist, album in rows:
        print(' | '.join(str(value).ljust(widths[i]) for i, value in enumerate((artist, album))))


d = discogs_client.Client('my_user_agent/1.0', user_token='QwlCQmTbbOmbvVichFkvbnXCKosnucLsSfWZCvoN')
me = d.identity()
print_artist_album_table(me.collection_folders[0].releases)