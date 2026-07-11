import html
from datetime import datetime
from pathlib import Path

import discogs_client


def format_artist_names(artists):
    if not artists:
        return 'Unknown artist'
    return ', '.join(getattr(artist, 'name', str(artist)) for artist in artists)


def normalize_text(value):
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return ', '.join(normalize_text(item) for item in value)
    if isinstance(value, dict):
        return ', '.join(f'{key}: {normalize_text(item)}' for key, item in value.items())
    return str(value)


def sort_key_for_added_date(value):
    value = normalize_text(value)
    if not value:
        return ''
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return value


def build_artist_album_rows(releases):
    rows = []
    for item in releases:
        release = getattr(item, 'release', None)
        if release is None:
            continue
        artist = normalize_text(format_artist_names(getattr(release, 'artists', [])))
        album = normalize_text(getattr(release, 'title', 'Unknown album'))
        item_data = getattr(item, 'data', {}) or {}
        release_id = normalize_text(item_data.get('id') or getattr(release, 'id', '') or '')
        added = normalize_text(item_data.get('date_added') or getattr(item, 'date_added', '') or '')
        notes = normalize_text(getattr(item, 'notes', '') or item_data.get('notes', '') or '')
        format_value = normalize_text(', '.join(
            getattr(fmt, 'name', str(fmt)) for fmt in getattr(release, 'formats', []) if fmt is not None
        ) or 'Unknown format')
        rows.append((artist, album, release_id, added, notes, format_value))

    return sorted(rows, key=lambda row: sort_key_for_added_date(row[3]), reverse=False)


def print_artist_album_table(rows):
    headers = ['artist', 'album', 'id', 'added date', 'notes', 'format']
    widths = [len(header) for header in headers]
    string_rows = [(str(artist), str(album), str(release_id), str(added), str(notes), str(format_value)) for artist, album, release_id, added, notes, format_value in rows]
    if string_rows:
        widths[0] = max(widths[0], max(len(artist) for artist, _, _, _, _, _ in string_rows))
        widths[1] = max(widths[1], max(len(album) for _, album, _, _, _, _ in string_rows))
        widths[2] = max(widths[2], max(len(release_id) for _, _, release_id, _, _, _ in string_rows))
        widths[3] = max(widths[3], max(len(added) for _, _, _, added, _, _ in string_rows))
        widths[4] = max(widths[4], max(len(notes) for _, _, _, _, notes, _ in string_rows))
        widths[5] = max(widths[5], max(len(format_value) for _, _, _, _, _, format_value in string_rows))

    print(' | '.join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print('-+-'.join('-' * width for width in widths))
    for artist, album, release_id, added, notes, format_value in string_rows:
        print(' | '.join(str(value).ljust(widths[i]) for i, value in enumerate((artist, album, release_id, added, notes, format_value))))


def save_artist_album_html(rows, output_path):
    rows_html = ''.join(
        f'<tr><td>{html.escape(artist)}</td><td>{html.escape(album)}</td><td>{html.escape(release_id)}</td><td>{html.escape(added)}</td><td>{html.escape(notes)}</td><td>{html.escape(format_value)}</td></tr>'
        for artist, album, release_id, added, notes, format_value in rows
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
    <tr><th>artist</th><th>album</th><th>id</th><th>added date</th><th>notes</th><th>format</th></tr>
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