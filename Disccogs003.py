import html
from pathlib import Path

import discogs_client


def format_artist_names(artists):
    if not artists:
        return 'Unknown artist'
    return ', '.join(getattr(artist, 'name', str(artist)) for artist in artists)


def build_artist_album_rows(releases):
    rows = []
    for item in releases:
        release = getattr(item, 'release', None)
        if release is None:
            continue
        artist = format_artist_names(getattr(release, 'artists', []))
        album = getattr(release, 'title', 'Unknown album')
        rows.append((artist, album))
    return rows


def print_artist_album_table(rows):
    headers = ['artist', 'album']
    widths = [len(headers[0]), len(headers[1])]
    string_rows = [(str(artist), str(album)) for artist, album in rows]
    if string_rows:
        widths[0] = max(widths[0], max(len(artist) for artist, _ in string_rows))
        widths[1] = max(widths[1], max(len(album) for _, album in string_rows))

    print(f"{headers[0].ljust(widths[0])} | {headers[1].ljust(widths[1])}")
    print(f"{'-' * widths[0]}-+-{'-' * widths[1]}")
    for artist, album in string_rows:
        print(f"{artist.ljust(widths[0])} | {album.ljust(widths[1])}")


def save_artist_album_html(rows, output_path):
    rows_html = ''.join(
        f'<tr><td>{html.escape(artist)}</td><td>{html.escape(album)}</td></tr>'
        for artist, album in rows
    )
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Discogs collection</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>Discogs collection</h1>
  <table>
    <tr><th>artist</th><th>album</th></tr>
    {rows_html}
  </table>
</body>
</html>
'''
    output_path.write_text(html_content, encoding='utf-8')
    return output_path


d = discogs_client.Client('my_user_agent/1.0', user_token='QwlCQmTbbOmbvVichFkvbnXCKosnucLsSfWZCvoN')
me = d.identity()
rows = build_artist_album_rows(me.collection_folders[0].releases)
print_artist_album_table(rows)
output_path = save_artist_album_html(rows, Path(__file__).with_suffix('.html'))
print(f'\nSaved HTML table to {output_path}')