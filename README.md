# xPress
xPress File archiver and extractor

# What is it?
xPress is a file compressor/archiver that stores data using a new type of compression algorithm called xPress. The xPress algorighm is very similar to LZW, but currently not as efficient. 

Currently xPress.py only supports files (not folders). File path arguments require absolute paths.

# How does it work?
xPress manages it's memory during compression by detecting system memory and chunking large files so they fit into memory. This still needs more testing to be sure it works on the largest of files (when filesize exceeds available memory). Otherwise compression would require (2 X "filesize") to compress, which isn't reasonable for extremely large files. By using this method compression only takes (2 X "chunkSize") which is much easier to live with.

During decompression xPress will exhaust available memory if the filesize is larger than available memory. As a result I expect large files to decompress faster than they compress.

# Why should I try it?

What makes xPress stand out from the crowd is that no configuration data gets embedded into an .xpr archive. So it doesn't matter what version, OS, or architecture, you used to compress your file. You could theoretically decompress your files manually (without a program) using simple copy/paste/replace functions in Notepad (although it would take a LOOOOOONG time).  

Decompression requires nothing special configuration-wise. The dictLength is inferred during decompression. This means any config settings are decompressible without knowing anything about how the file was compressed.

# Where should I start?

There's some example commands in Example_Commands.txt, bu here's a quick rundown...

## Usage

If you combine multiple verbosity or log levels the last specified will be used.

*h - Display help text. 1st argument.
*c - Convert. 1st argument.
*e - Extract. 1st argument.

*C:\Path\To\Input_File - 2nd argument.

*C:\Path\To\Output_File - 3rd argument

*v0 - Verbosity 0. Optional. Disable output. 4th or 5th argument.
*v1 - Verbosity 1. Optional. Only errors are output. 4th or 5th argument.
*v2 - Verbosity 2. Optional. Everything is output. 4th or 5th argument.

*l0 - Log level 0. Optional. Disable logging. 4th or 5th argument.
*l1 - Log level 1. Optional. Only errors logged. 4th or 5th argument. 
*l2 - Log level 2. Optional. Everything is logged. 4th or 5th argument.

## Examples

Compress test.txt, create output.xpr, use log level 0, use verbosity level 2.
*xPress.py c C:\Users\Test\Desktop\test.txt C:\Users\Test\Desktop\output.xpr v0 l2

Extract test.xpr, create output.txt, use log level 1, use verbosity level 0.
*xPress.py e C:\Users\Test\Desktop\test.xpr C:\Users\Test\Desktop\output.txt l1 v0

Display help text.
*xPress.py h

# Anything else?

Please check out the code and help me make it better. I know the field of data compression is a science that I'm just scratching the surface of and I would greatly appreciate any feedback.

xPress.py is an [HonestRepair](https://www.HonestRepair.net/) project by Justin Grimes (@zelon88).
