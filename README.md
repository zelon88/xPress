# xPress
xPress File archiver and extractor

Experimental! Currently only supports files (not folders). File path arguments require absolute paths.

Currently there is no hueristics to determine the dictionary length. dictLength is hard-coded as a variable in the start of the script. Longer dictionary lengths are better for larger files. Smaller dictionary lengths are better for smaller files. I intend to add code for automatically detecting what dictLength to use. First I have to experiment and figure out what baselines will work well.

xPress manages it's memory during compression by detecting system memory and chunking large files so they fit into memory. This still needs more testing to be sure it works on the largest of files (when filesize exceeds available memory). Otherwise compression would require (2 X "filesize") to compress, which isn't reasonable for extremely large files. By using this method compression only takes (2 X "chunkSize") which is much easier to live with.

During decompression xPress will exhaust available memory if the filesize is larger than available memory. As a result I expect large files to decompress faster than they compress.

Decompression requires nothing special configuration-wise. The dictLength is inferred during decompression, so no config data gets embedded into the archive. This means any config settings are decompressible without knowing anything about how the file was compressed.

Please check out the code and help me make it better. I know the field of data compression is a science that I'm just scratching the surface of and I would greatly appreciate any feedback.
