# Convert to Webp
C2W is a app for converting image files of the most common formats to webp. To choose between lossless and lossy is possible.
Supported formats are:
- png
- jpeg
- tiff
- gif
- webp

The latter is also mentioned because it can be reconverted in a different(lower) quality setting.

There are three different coding try's/concepts here for this:

* Variant 1: `convert2webp_v1.py`
    Is the oldest version but should work.
* Variant 2: `convert2webp_v2.py`
    Like v1 and a little bit overhauled, but uses a python class.

    Note: Converting of animated gif images is deactivated because the encoder is bugged.
    Images come with to slow playback out of it.
