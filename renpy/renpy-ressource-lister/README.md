# Ren'py Ressource Lister
A python script that lists images, audio and video in a file for use in a
project developed with the ren'py engine.


## Description

The python script finds and filters a projects images and audio (only
supported mimetypes). It lists these then as ready-for-use defined ren'py
statements in a file.

As a welcome addition, the output can be used as summary of your directory
structure and assets.

### Requirements
*   python 3 or higher
    -   python-magic
    -   natsort
*   Ren'py

_Ren'py is more optional but without it there is no real use for the output._

### Usage

Position the file in your games "game" directory and add the executable flag.
Execute the script then in a shell **with one or more** of the required
arguments.
If no optional options given the script uses the following standards:
*   Image directory: **images**
*   Audio directory: **audio**
*   Video directory: **video**
*   Output file: **ressource_def.rpy**

```
Switches:
  One of the options is required.
  -i                   Activate search and listing of images
  -a                   Activate search and listing of audio
  -v                   Activate search and listing of video

optional arguments:
  -idir IMAGE_RES_DIR  Name of the image folder
  -adir AUDIO_RES_DIR  Name of the audio folder
  -vdir VIDEO_RES_DIR  Name of the video folder
  -o OUTPUT_FILE       Name for the output file
  --version            show program's version number and exit
  --help, -h           Show this help message and exit

$ python3 rpy_res_def.py -i -a -v -idir <image-dir> -adir <audio-dir> -vdir <video-dir> -f <output.rpy>
$
```

### Version
*   Version 0.7.0-alpha

## Author
*   Website: <https://github.com/madeddy>


## License
This work is distributed under the MIT license, as described in the LICENSE.md
file.
