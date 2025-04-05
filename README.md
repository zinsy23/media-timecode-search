# Media Timecode Search

This project is designed to reference transcript files between two versions of media (i.e. a livestream and the edited version of that livestream) so the user can enter the timecode of one of those sources to find the corresponding timecode in the other source. It can also be useful when trying to reference a specific moment across two versions of media in general and the timings aren't directly parallel.

## Setup

1. Install the dependencies:
```sh
pip install -r requirements.txt
```

2. If you're referencing the subtitles locally, create a new directory for the subtitles in the same directory as the script. If you're referencing the subtitles from the cloud, see the [Connecting to the Cloud](#connecting-to-the-cloud-the-way-i-do-it) section.

3. Add the two corresponding transcripts in the "subtitles" location. Name them using the following format convention: `media_basename sourcetype` (e.g. `time_travel_audio edited.srt`)

**Note**: The label for the source and destination can be pretty much any terminology pair. It can be edited and livestream, source and destination, before and after, original and edited, etc.

## Usage

1. Run the script and provide it the media name, based on the base name of the subtitles. (`python find_timecode.py [subtitle_basename] [time] ?[source|dest]`)

Example:
```sh
python find_timecode.py time_travel_audio 1:36:14
```
Example output:
```sh
2:02:24
```

**Note**: You can also invert the default direction of the source and destination by using the third argument. For example, if you want to find the corresponding time for the edited version instead of the live version by default, you can use the following command:
```sh
python find_timecode.py time_travel_audio 1:36:14 edited
```
In this case, if edited weren't provided in the above command, the script would have done the live version instead.

## Connecting to the Cloud (my process)

1. Set the `SOURCE_TYPE` variable to `cloud` in the `media_timecode.py` file.

2. Create a cloud bucket for the subtitles using a compatible cloud service, such as Cloudflare R2 or Amazon S3.

3. Add your service API keys to a secrets manager, such as [Doppler](https://www.doppler.com/). Ensure the names match the variables in the `CLOUD_RESOURCE` variable in the `media_timecode.py` file. Create a project in Doppler and add the keys to the project (I'm using mine in the prd config).

4. Install [Doppler CLI](https://docs.doppler.com/docs/install-cli) and run `doppler login` once installed.

5. Once logged in, set up Doppler by running `doppler setup` and follow the prompts to point to your project. 

6. Ensure the environment varaibles in `CLOUD_RESOURCE` from `media_timecode.py` match what it is set to in Doppler.

7. When you run the script with Doppler, run it as `doppler run -- python find_timecode.py [subtitle_basename] [time] ?[source|dest]`.

**Example**: `doppler run -- python find_timecode.py time_travel_audio 1:36:14 edited`

## Docker Setup Process (if used)

1. From the main project directory, build the Docker image:
```sh
docker build -t media-timecode-search .
```

2. Run the Docker container.

To run it interactively in PowerShell, referencing the subtitles locally, run the following command:
```sh
docker run -it --mount "type=bind,source=${PWD}\subtitles,target=/home/python/media-timecode-search/subtitles" media-timecode-search
```

To run it interactively in PowerShell, referencing the subtitles from the cloud using Doppler, set up a service token in Doppler. Set up the cloud if not done so already, referencing the [Connecting to the Cloud](#connecting-to-the-cloud-the-way-i-do-it) section. Add it to the `dev` config in Doppler (if using in local development), preferably called `DOPPLER_TOKEN`.

Then, run the following commands:
```sh
$DOPPLER_TOKEN = doppler secrets get DOPPLER_TOKEN --raw --plain --config dev
```
then:
```sh
docker run -it -e DOPPLER_TOKEN="$DOPPLER_TOKEN" media-timecode-search
```
This will allow program in the container to securely access the Doppler secrets for connecting to the cloud. 

 **Note**: Don't forget to set the `SOURCE_TYPE` variable to `cloud` in the `media_timecode.py` file if not already set.
 You also only need to define `$DOPPLER_TOKEN` environment variable once per shell session.