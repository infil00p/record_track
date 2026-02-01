import requests
from bs4 import BeautifulSoup
import datetime
import subprocess
import time
import sys
import re
import os
import argparse

def get_schedule(track_url):
    print(f"Fetching schedule from {track_url}...")
    r = requests.get(track_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, 'html.parser')
    
    events = []
    rows = soup.find_all('tr')
    
    for tr in rows:
        cells = tr.find_all('td')
        if not cells or len(cells) < 5:
            continue
            
        # Title is usually in the second cell (index 1)
        title_cell = cells[1]
        title_link = title_cell.find('a')
        if not title_link:
            continue
        title = title_link.get_text(strip=True)
        
        # Start/End times
        start_cell = cells[3]
        end_cell = cells[4]
        
        start_link = start_cell.find('a', title=True)
        end_link = end_cell.find('a', title=True)
        
        if start_link and end_link:
            start_iso = start_link['title'] # e.g., 2026-01-31T10:30:00+01:00
            end_iso = end_link['title']
            
            start_dt = datetime.datetime.fromisoformat(start_iso)
            end_dt = datetime.datetime.fromisoformat(end_iso)
            
            events.append({
                'title': title,
                'start': start_dt,
                'end': end_dt
            })
            
    return events

def sanitize_filename(name):
    return re.sub(r'[^\w\-_]', '_', name)

def record_stream(duration, filename, stream_url):
    print(f"Recording for {duration} seconds to {filename}...")
    cmd = [
        'ffmpeg',
        '-y',
        '-i', stream_url,
        '-c', 'copy',
        '-t', str(duration),
        filename
    ]
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description='Record FOSDEM track streams.')
    parser.add_argument('track_url', help='URL of the track schedule (e.g., https://fosdem.org/2026/schedule/track/ai/)')
    parser.add_argument('stream_url', help='URL of the stream (e.g., https://stream.fosdem.org/ud2120.m3u8)')
    parser.add_argument('--name', help='Optional prefix/name for the track', default='')
    parser.add_argument('--dry-run', action='store_true', help='Print schedule without recording')
    
    args = parser.parse_args()
    
    try:
        events = get_schedule(args.track_url)
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return

    print(f"Found {len(events)} events.")
    
    events.sort(key=lambda x: x['start'])
    
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    
    # Create output directory
    output_dir = args.name if args.name else sanitize_filename(args.track_url.split('/')[-2])
    if not args.dry_run and output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Saving recordings to {output_dir}/")

    for event in events:
        start = event['start']
        end = event['end']
        duration = (end - start).total_seconds()
        
        safe_title = sanitize_filename(event['title'])
        # Filename only needs time and title, folder handles the track name
        filename = f"{start.strftime('%H%M')}_{safe_title}.mp4"
        filepath = os.path.join(output_dir, filename)
        
        print(f"\nEvent: {event['title']}")
        print(f"  Start: {start}")
        print(f"  End:   {end}")
        print(f"  Duration: {duration}s")
        print(f"  File: {filepath}")
        
        if args.dry_run:
            continue
            
        if end < now:
            print("  Event finished, skipping.")
            continue
            
        wait_seconds = (start - now).total_seconds()
        if wait_seconds > 0:
            print(f"  Waiting {wait_seconds:.0f} seconds to start...")
            time.sleep(wait_seconds)
        else:
            print("  Event in progress, recording remaining time...")
            remaining = (end - datetime.datetime.now(start.tzinfo)).total_seconds()
            if remaining <= 0:
                 print("  Event just finished, skipping.")
                 continue
            duration = remaining

        try:
            record_stream(duration, filepath, args.stream_url)
        except subprocess.CalledProcessError as e:
            print(f"  Recording failed: {e}")
        except KeyboardInterrupt:
            print("  Recording stopped by user.")
            break
            
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()

if __name__ == "__main__":
    main()
