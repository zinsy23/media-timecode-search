# Media Timecode Search

This project is designed to reference transcript files between two versions of media (i.e. a livestream and the edited version of that livestream) so the user can enter the timecode of one of those sources to find the corresponding timecode in the other source. It can also be useful when trying to reference a specific moment across two versions of media in general and the timings aren't directly parallel.

## Usage

1. Add the two corresponding transcripts in the "subtitles" directory.
2. Run the script and provide it the media name, based on the base name of the subtitles. (`[script] [subtitle_basename] [time] [?source|dest]`)

Example:
```sh
find_timecode.py time_travel_audio 1:36:14
```
Example output:
```sh
2:02:24
```