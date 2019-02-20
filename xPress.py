# --------------------------------------------------
# xPress.py
# v0.9.1 - 2/20/2019
#
# Justin Grimes (@zelon88)
#   https://github.com/zelon88/xPress
#   https://www.HonestRepair.net
#
# Made on Windows 7 with Python 2.7.12
#
# This program is a file compressor and extractor that uses
# a new compression algorithm designed and dictated by this 
# document. It has an adjustable dictionary value length and
# can decompress files without special extractor preparations.

# Code comments are prefaced with COMPRESS or EXTRACT to denote
# which function they support, for easier code surfing. 
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Load required modules and set global variables.
import sys, getopt, datetime, os, binascii, psutil, math, pickle, re
now = datetime.datetime.now()
time = now.strftime("%B %d, %Y, %H:%M")
error = ''
inputFile = ''
inputPath = ''
dictFile = ''
dictPath = ''
tempFile = ''
tempPath = ''
outputFile = ''
outputPath = ''
chunkSize = 0
offset = 0
chunkCount = 0
dictLength = 12
dictionaryPreffix = '@!@!@!DICTSTART@!@!@!'
dictionarySuffix = '@!@!@!DICTEND@!@!@!'
print ("\n"+'OP-Act: Starting xPress Compress on '+str(time)+'!'+"\n")
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Process user supplied arguments.
def parseArgs(argv):
  # Check if any arguments were passed.
  try:
    opts, args = getopt.getopt(argv,"h")
  except getopt.GetoptError:
    print ('xPress.py <c>or<e> <inputFile> <outputFile>')
    sys.exit(2)
  if sys.argv[1] == 'c':
    feature = 'compress'
  if sys.argv[1] == 'e':
    feature = 'extract'
  # Check to see if an input file argument was supplied.
  try:
    sys.argv[1]
  except IndexError:
    # Display an error and stop execution if the input argument is missing.
    print ('ERROR!!! xPress48, No input file was specified on '+str(time)+'!')
    sys.exit()
  else:
    inputFile = sys.argv[2]
    inputPath = os.path.dirname(inputFile)
    # Check to see that a directory exists to put an output file into.
    if not os.path.exists(inputFile):
      print ('ERROR!!! xPress55, The input file specified does not exist on '+str(time)+'!')
      sys.exit()
  # Check to see if an output file argument was supplied.
  try:
    sys.argv[3]
  except IndexError:
    # Display an error and stop execution if the output argument is missing.    
    print ('ERROR!!! xPress34, No output file was specified on '+str(time)+'!')
    sys.exit()
  else: 
    outputFile = sys.argv[3]
    outputPath = os.path.dirname(outputFile)
    tempFile = sys.argv[3]+'-TEMP.dat'
    tempPath = os.path.dirname(tempFile)
    dictFile = sys.argv[3]+'-DICT.dat'
    dictPath = os.path.dirname(dictFile)
    # Check to see that a directory exists to put an output file into.
    if not os.path.exists(outputPath):
      print ('ERROR!!! xPress41, The output file specified relies on an invalid directory on '+str(time)+'!')
      sys.exit()
  return tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Define the chunkSize based on fileSize and available memory.
# We need to store 2 copies of the offset buffer and the rest of this application.
# By dynamically setting how much of a file to load into memory at a time, xPress should be hardware agnostic.
# Severely limited machines with memory levels measured in hundreds of megabytes may see less compression performance than machines with more memory.
def defineChunkSize(inputFile):
  chunkSize = 0
  # Get the filesize of the input file.
  print ('OP-Act: Defining chunkSize with inputFile of '+str(inputFile))
  fileSize = int(os.path.getsize(inputFile))
  # Get the available memory.
  mem = psutil.virtual_memory()
  availableMemory = mem.available
  print ('OP-Act: Available memory is '+str(availableMemory))
  # Our chunkSize is 1/4 of available memory. This translates to about 1/2 of available memory used once we load each chunk twice.
  chunkSize = int(availableMemory) / 4
  # If the chunkSize is smaller than the file being processed the entire file becomes the only chunk.
  if chunkSize >= fileSize:
    chunkSize = fileSize
  print ('OP-Act: ChunkSize is '+str(chunkSize))
  return chunkSize
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Define what the file offsets and number of chunks based on fileSize and chunkSize.
# If a file is too big it is divided into small chunks.
# The offset is different from the chunkSize in that it is evenly divisible by the filesize.
# To put it differently, the chunkSize limits global memory usage and the offset allocates an exact quantity of memory for each operation.
def defineOffset(inputFile, chunkSize):
  offset = chunkCount = result = 'ERROR'
  # Verify that the inputFile exists.
  if os.path.isfile(inputFile):
    # Get the filesize of the input file.
    fileSize = int(os.path.getsize(inputFile))
    chunkSize = int(chunkSize)
    print ('OP-Act: Defining offset with chunkSize of '+str(chunkSize))
    # Decide if the file should be chunked or processed as a whole.
    if fileSize > chunkSize:
      chunkCount = int(math.ceil(fileSize / chunkSize))
      offset = fileSize
    else:
      chunkCount = 1
    offset = fileSize / chunkCount
    result = 1
    print ('OP-Act: Offset is '+str(offset)+', chunkCount is '+str(chunkCount))
  else:
    offset = chunkCount = result = 'ERROR'
    chunkCount = 0
  return offset, chunkCount, result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function to iterate through the temp file and build a dictionary for the file.
def buildDictionary(outputFile, inputFile, dictFile, dictLength, dictionaryPreffix, dictionarySuffix):
  dictionary = result = data = 'ERROR'
  # Verify that no output file or dict file exists already.
  if os.path.isfile(outputFile) or os.path.isfile(dictFile):
    print ('ERROR!!! xPress123, The output file or temp files already exist for outputFile '+str(outputFile)+' on '+str(time)+'!')
  else:
    # Verify that in input file exists.
    if os.path.isfile(inputFile):
      result = 1
      print ('OP-Act: Building a dictionary with inputFile '+str(inputFile))
      dictionary = {}
      dictCount = 0
      dictIndexNumber = 0
      dictIndex = '#',str(dictIndexNumber),'$'
      counter0 = 0
      tempChunkSize = defineChunkSize(inputFile)
      tempOffset, tempChunkCount, dOffResult = defineOffset(inputFile, tempChunkSize)
      if dOffResult != 'ERROR' and tempOffset != 'ERROR' and tempChunkCount > 0:
        # Open the input file.
        with open(inputFile, "rb") as openFile:
          while counter0 < tempChunkCount:
            # Set the current offset.
            filePosition = openFile.tell()
            # Fill up the offset buffer.
            data = openFile.read(tempOffset)
            # Select some data and attempt to compress it.
            for i in xrange(0, len(data), dictLength):
              print ('OP-Act: Initiating a compression loop.'+str(i))
              chars = data[i:(i+dictLength)]
              if data.find(chars) >= 0:
                dictIndexNumber += 1
                dictIndex = '#'+str(dictIndexNumber)+'$'
                data = data.replace(chars, dictIndex)
                dictionary.update({dictIndex : chars})
                # Save the compressed data to the output file.
                with open(outputFile, "wb") as openFile2:
                  openFile2.write(data)
                  openFile2.close()
              else:
                # Save uncompressed data to the output file.
                with open(outputFile, "wb") as openFile2:
                  openFile2.write(data)
                  openFile2.close()
              counter0 += 1
          openFile.close()
          with open(dictFile, "wb") as openFile3:
            openFile3.write(str(dictionary))
            openFile3.close()
      else:
        dictionary = result = data = 'ERROR'
    else: 
      dictionary = result = data = 'ERROR'
  # Verify that a dictionary file was created and no errors were encountered.
  if not os.path.isfile(dictFile) or dictionary == 'ERROR' or result == 'ERROR':
    dictionary = result = data ='ERROR'
    print ('ERROR!!! xPress173, The operation failed to generate a dictionary for inputFile '+str(inputFile)+' on '+str(time)+'!')
  return dictionary, data, result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function to iterate through the temp file and compress its actual data using the dictionary.
def compressFile(outputFile, compressedData, dictionary, dictionaryPreffix, dictionarySuffix):
  print ('OP-Act: Writing dictionary to outputFile '+outputFile)
  archive = open(outputFile, "ab")
  archive.write(dictionaryPreffix)
  pickle.dump(dictionary, archive)
  archive.write(dictionarySuffix)
  archive.close()
  result = 1
  # Verify that an output file was created.
  if not os.path.isfile(outputFile):
    result = 'ERROR'
    print ('ERROR!!! xPress232, The operation failed to write the dictionary to outputFile'+str(outputFile)+' on '+str(time)+'!')
  return result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to extract compressed data and reconstruct the dictionary file.
def extractDictionary(inputFile, outputFile, dictFile, dictionaryPreffix, dictionarySuffix):
  result = dictionary = data = 'ERROR'
  # Perform sanity checks before attempting anything.
  if os.path.isfile(outputFile) or os.path.isfile(dictFile):
    print ('ERROR!!! xPress240, The output file or temp files already exist for outputFile '+str(outputFile)+' on '+str(time)+'!')
  else:
    if os.path.isfile(inputFile):
      print ('OP-Act: Extracting dictionary from inputFile '+str(inputFile))
      # Open the input file and put its contents into memory.
      with open(inputFile, 'rb') as inputData:
        inData = inputData.read()
        # Extract the dictionary data from the input data.
        dictionaryData = inData[inData.find(dictionaryPreffix)+len(dictionaryPreffix):inData.find(dictionarySuffix)]
        inData = inData.replace(dictionaryData, '').replace(dictionaryPreffix, '').replace(dictionarySuffix, '')
        dictionaryData = dictionaryData.replace(dictionaryPreffix, '').replace(dictionarySuffix, '')
        inputData.close()
      # Write the extracted dictionary data to a temporary dictionary file.
      with open(dictFile, 'wb') as dictData:
        dictData.write(dictionaryData)
        dictData.close()
        # Create an output file, separate compressed data from dictionary data, and put just the compressed data into it.
      with open(outputFile, 'wb') as outputData:
        outputRaw = inData.replace(dictionaryPreffix+dictionaryData+dictionarySuffix, '')
        outputData.write(outputRaw)
        outputData.close()
      dictFileOpen = open(dictFile, "rb")
      dictionary = pickle.load(dictFileOpen)
      dictFileOpen.close()
      data = outputRaw
      result = 1
    else:
      result = dictionary = data = 'ERROR'
      print ('ERROR!!! xPress254, The operation failed to extract a dictionary from inputFile '+str(inputFile)+' on '+str(time)+'!')
  if not os.path.isfile(dictFile):
    result = dictionary = data = 'ERROR'
    print ('ERROR!!! xPress232, The operation failed to write the dictionary to outputFile'+str(outputFile)+' on '+str(time)+'!')
  return dictionary, data, result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to loop through the dictionary and compressed data and look for matches.
def dictionaryLoop(compressedData, dictionary):
  result = 'ERROR'
  matchCount = 0
  if not isinstance(dictionary, dict):
    print ('ERROR!!! xPress285, The supplied dictionary is not readable on '+str(time)+'!')
  else:
    result = 1
    #print ('OP-Act: Beginning data decompression loop.')
    # Loop through each key in the dictionary, count and replace matches.
    for key, value in dictionary.iteritems():
      #print ('OP-Act: Iterating through dictionary with key '+str(key)+' and value '+str(value))
      matchCount = matchCount + compressedData.count(key)
      compressedData = compressedData.replace(key, value)
      print matchCount
  return compressedData, dictionary, matchCount, result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to decompress an input file.
def decompressFile(outputFile, compressedData, dictionary):
  result = 'ERROR'
  counter = 1
  decompressedData = ''
  if not os.path.isfile(outputFile) or compressedData == 'ERROR' or dictionary == 'ERROR':
    print ('ERROR!!! xPress294, Could not decompress outputFile '+str(outputFile)+' on '+str(time)+'!')
  else:
    result = 1
    print ('OP-Act: Initiating decompressor on inputFile '+str(inputFile))
    # Loop through the file and look for dictionary matches.
    while counter != 0:
      compressedData, dictionary, counter, result = dictionaryLoop(compressedData, dictionary)
      if result == 'ERROR' or compressedData == 'ERROR':
        print ('ERROR!!! xPress311, The operation failed during decompression of outputFile '+str(outputFile)+' on '+str(time)+'!')
    with open(outputFile, 'wb') as outputData:
      outputData.write(compressedData)
      outputData.close()
    if not os.path.isfile(outputFile):
      result = 'ERROR'
      print ('ERROR!!! xPress315, The operation failed to create an outputFile '+str(outputFile)+' on '+str(time)+'!')
    else:
      result = 1
  return result 
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Code to compress a specified file.
if sys.argv[1] == 'c':
  tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath = parseArgs(sys.argv[1:])  
  dictionary, compressedData, dictResult = buildDictionary(outputFile, inputFile, dictFile, dictLength, dictionaryPreffix, dictionarySuffix)
  if dictResult != 'ERROR':
    compressionResult = compressFile(outputFile, compressedData, dictionary, dictionaryPreffix, dictionarySuffix)
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# Code to extract a specified file.
if sys.argv[1] == 'e':
  tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath = parseArgs(sys.argv[1:])  
  dictionary, compressedData, dictResult = extractDictionary(inputFile, outputFile, dictFile, dictionaryPreffix, dictionarySuffix)
  if dictResult != 'ERROR':
    decompressionResult = decompressFile(outputFile, compressedData, dictionary)
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
print ("\n")
# --------------------------------------------------