# Media Timecode Search

This project is designed to reference transcript files between two versions of media (i.e. a livestream and the edited version of that livestream) so the user can enter the timecode of one of those sources to find the corresponding timecode in the other source. It can also be useful when trying to reference a specific moment across two versions of media in general and the timings aren't directly parallel.

## Setup

1. Install the dependencies:
```sh
pip install -r requirements.txt
```

2. If you're referencing the subtitles locally, create a new directory for the subtitles in the same directory as the script. If you're referencing the subtitles from the cloud, see the [Connecting to the Cloud](#connecting-to-the-cloud-my-process) section.

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

4. Create a service token in Doppler and add it to the `dev` config (if using local Docker environment), preferably called `DOPPLER_TOKEN`. Ensure Doppler CLI is pointing to the dev config passing into containers so it can be accessed via Doppler in the container. Set it via `doppler setup` in the local environment and follow the prompts.

5. Install [Doppler CLI](https://docs.doppler.com/docs/install-cli) and run `doppler login` once installed.

6. Once logged in, set up Doppler by running `doppler setup` and follow the prompts to point to your project. 

7. Ensure the environment variables in `CLOUD_RESOURCE` from `media_timecode.py` match what it is set to in Doppler.

8. When you run the script with Doppler, run it as `doppler run -- python find_timecode.py [subtitle_basename] [time] ?[source|dest]`.

**Example**: `doppler run -- python find_timecode.py time_travel_audio 1:36:14 edited`

## If Running The Website Using Docker:

1. If you don't already have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine, install it.

**Note**: If you're having issues with Docker Desktop on Windows due to WSL related issues, I recommend fully uninstalling and reinstalling using the Hyper-V option instead of WSL. It's likely not worth screwing around with.

2. Set up a Doppler service token in the project as indicated in the [Connecting to the Cloud](#connecting-to-the-cloud-my-process) section, step 4.

3. Create a `.env` file in the project directory and add the `DOPPLER_TOKEN` variable. See the [Connecting to the Cloud](#connecting-to-the-cloud-my-process) section for more information on setting up Doppler and getting the token. You can rename the `.env.example` file to `.env` and add your token to it. Ensure the token never gets shared as it needs to be defined in the `.env` file in plain text.

4. If you're referencing the subtitles locally instead of on the cloud, you can set the `SOURCE_TYPE` variable to `local` in the `media_timecode.py` file. There should already be a bind mount for the subtitles directory in the `docker-compose.yml` file. Create the subtitles directory in the project directory if it doesn't already exist. See the [Setup](#setup) section for more information on the subtitle file naming convention.

5. If you're referencing the subtitles from the cloud, you can set the `SOURCE_TYPE` variable to `cloud` in the `media_timecode.py` file. Connect to the cloud, referencing the [Connecting to the Cloud](#connecting-to-the-cloud-my-process) section.

6. Once everything is set up, run the following command to install and start the containers:
```sh
docker compose up -d
```

7. You can then access the website at `http://localhost:8000`.

8. To turn it off, run the following command:
```sh
docker compose down
```

## If Using Docker Without Docker Compose:

1. If you don't already have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine, install it.

**Note**: If you're having issues with Docker Desktop on Windows due to WSL related issues, I recommend fully uninstalling and reinstalling using the Hyper-V option instead of WSL. It's likely not worth screwing around with.

2. From the main project directory, build the Docker image:
```sh
docker build -t media-timecode .
```

3. Run the Docker container.

To run it interactively in PowerShell, referencing the subtitles locally, run the following command:
```sh
docker run -it --mount "type=bind,source=${PWD}\subtitles,target=/home/python/media-timecode-search/subtitles" media-timecode
```

To run it interactively in PowerShell, referencing the subtitles from the cloud using Doppler, set up the cloud and a service token in Doppler if you've not done so already, referencing the [Connecting to the Cloud](#connecting-to-the-cloud-my-process) section, step 4. 

Then, run the following commands:
```sh
$DOPPLER_TOKEN = doppler secrets get DOPPLER_TOKEN --raw --plain --config dev
```
then:
```sh
docker run -it -e DOPPLER_TOKEN="$DOPPLER_TOKEN" media-timecode
```
This will allow program in the container to securely access the Doppler secrets for connecting to the cloud. 

 **Notes**: Don't forget to set the `SOURCE_TYPE` variable to `cloud` in the `media_timecode.py` file if not already set. 
 
 You also only need to define `$DOPPLER_TOKEN` environment variable once per shell session. 
 
 It's also not recommended to run the website container without the docker compose solution, so use docker compose if using with the website.