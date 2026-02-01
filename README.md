# FOSDEM Stream Recorder

A Python script to automatically record talks from FOSDEM live streams based on the schedule.

## Prerequisites

- Python 3
- `ffmpeg` installed and in your PATH
- `requests` and `beautifulsoup4` python libraries:
  ```bash
  pip install requests beautifulsoup4
  ```

## Usage

The `record_track.py` script waits for talks to start (based on the schedule) and records them to individual `.mp4` files.

```bash
python3 record_track.py <TRACK_SCHEDULE_URL> <STREAM_URL> --name <FOLDER_NAME>
```

-   `<TRACK_SCHEDULE_URL>`: The URL of the track's schedule on fosdem.org.
-   `<STREAM_URL>`: The `.m3u8` stream URL (found on the live stream page).
-   `--name`: (Optional) Name for the output folder and file prefix. Files will be saved in a folder with this name.

### Examples

**AI Plumbers Track:**
```bash
python3 record_track.py https://fosdem.org/2026/schedule/track/ai/ https://stream.fosdem.org/ud2120.m3u8 --name AI_Plumbers
```

**Browser & Web Platform Track:**
```bash
python3 record_track.py https://fosdem.org/2026/schedule/track/browser-and-web-platform/ https://stream.fosdem.org/h1309.m3u8 --name Browser
```

**FOSS on Mobile Track:**
```bash
python3 record_track.py https://fosdem.org/2026/schedule/track/foss-on-mobile/ https://stream.fosdem.org/ub4132.m3u8 --name FOSS_on_Mobile
```

## Output

The script creates a folder matching the `--name` argument (e.g., `AI_Plumbers/`) and saves files named with the format: `HHMM_Talk_Title.mp4`.
