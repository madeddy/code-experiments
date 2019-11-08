# Convert2webp
C2W is a app for converting image files of the most common formats to webp. To choose between lossless and lossys is possible.
Supported formats are:
- png
- jpeg
- tiff
- gif
- webp
The latter is mentioned because it can be reconverted in a different quality setting.

There are three different coding try's/concepts here for this:

* Variant 1: `convert2webp.py` Is the oldest version but should work.
* Variant 2: `convert2webp_cls.py` Like 1 and a little bit overhauled, but uses a python class.
* Variant 3: `convert2webp_cls_mt.py` Like 2 but with mutithreading. Quit useful if a massconvert is done.
