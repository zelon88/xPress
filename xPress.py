# --------------------------------------------------
# xPress.py
# v0.8.5 - 2/16/2019
#
# Justin Grimes (@zelon88)
#   https://github.com/zelon88
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
import sys, getopt, datetime, os, binascii, psutil, math, pickle
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
print ("\n"+'OP-Act: Starting xPress Compress!'+"\n")
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
    print ('ERROR!!! xPress48, No input file was specified on '+time+'!')
    sys.exit()
  else:
    inputFile = sys.argv[2]
    inputPath = os.path.dirname(inputFile)
    # Check to see that a directory exists to put an output file into.
    if not os.path.exists(inputFile):
      print ('ERROR!!! xPress55, The input file specified does not exist on '+time+'!')
      sys.exit()
  # Check to see if an output file argument was supplied.
  try:
    sys.argv[3]
  except IndexError:
    # Display an error and stop execution if the output argument is missing.    
    print ('ERROR!!! xPress34, No output file was specified on '+time+'!')
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
      print ('ERROR!!! xPress41, The output file specified relies on an invalid directory on '+time+'!')
      sys.exit()
  return tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Define the chunkSize based on fileSize and available memory.
# We need to store 2 copies of the offset buffer and the rest of this application.
# By dynamically setting how much of a file to load into memory at a time, xPress should be hardware agnostic.
# Severely limited machines with memory levels measured in hundreds of megabytes may see less compression performance than machines with more memory.
def defineChunkSize(inputFile):
  # Get the filesize of the input file.
  print ('OP-Act: Defining chunkSize with inputFile of '+inputFile)
  fileSize = int(os.path.getsize(inputFile))
  # Get the available memory.
  mem = psutil.virtual_memory()
  availableMemory = mem.available
  print('OP-Act: Available memory is '+str(availableMemory))
  # Our chunkSize is 1/4 of available memory. This translates to about 1/2 of available memory used once we load each chunk twice.
  chunkSize = int(availableMemory) / 4
  # If the chunkSize is smaller than the file being processed the entire file becomes the only chunk.
  if chunkSize >= fileSize:
    chunkSize = fileSize
  print ('OP-Act: ChunkSize is '+str(chunkSize))
  return chunkSize
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Define what the file offsets and number of chunks based on fileSize and chunkSize.
# If a file is too big it is divided into small chunks.
# The offset is different from the chunkSize in that it is evenly divisible by the filesize.
# To put it differently, the chunkSize limits global memory usage and the offset allocates an exact quantity of memory for each operation.
def defineOffset(inputFile, chunkSize):
  result = 'ERROR'
  if os.path.isfile(inputFile):
    # Get the filesize of the input file.
    fileSize = int(os.path.getsize(inputFile))
    chunkSize = int(chunkSize)
    print ('OP-Act: Defining offset with chunkSize of '+str(chunkSize))
    if fileSize > chunkSize:
      chunkCount = int(math.ceil(fileSize / chunkSize))
      offset = fileSize
    else:
      chunkCount = 1
    offset = fileSize / chunkCount
    result = 1
    print('OP-Act: Offset is '+str(offset)+', chunkCount is '+str(chunkCount))
  else:
    offset = result = 'ERROR'
    chunkCount = 0
  return offset, chunkCount, result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function to iterate through the temp file and build a dictionary for the file.
def buildDictionary(outputFile, inputFile, dictFile):
  result = 'ERROR'
  if os.path.isfile(outputFile) or os.path.isfile(dictFile):
    print ('ERROR!!! xPress123, The output file or temp files already exist for outputFile '+outputFile+'!')
    dictionary = result = 'ERROR'
    data = ''
  else:
    if os.path.isfile(inputFile):
      result = 1
      print ('OP-Act: Building a dictionary with inputFile '+inputFile)
      dictionary = {}
      dictCount = 0
      dictIndexNumber = 0
      dictIndex = '#',str(dictIndexNumber),'$'
      counter0 = 0
      tempChunkSize = defineChunkSize(inputFile)
      tempOffset, tempChunkCount, dOffResult = defineOffset(inputFile, tempChunkSize)
      if dOffResult != 'ERROR' and tempOffset != 'ERROR' and tempChunkCount > 0:
        # Open the input file.
        with open(inputFile, "r") as openFile:
          while counter0 < tempChunkCount:
            # Set the current offset.
            filePosition = openFile.tell()
            # Fill up the offset buffer.
            data = openFile.read(tempOffset)
            # Select some data and attempt to compress it.
            for i in xrange(0, len(data), 20):
              chars = data[i:i+20]
              if data.find(chars) >= 0:
                dictIndexNumber += 1
                dictIndex = '#'+str(dictIndexNumber)+'$'
                data = data.replace(chars, dictIndex)
                dictionary.update({dictIndex : chars})
                # Decide whether we need to create a new output file or append to an existing one.
                if os.path.isfile(outputFile):
                  appendWrite = "ab"
                else:
                  appendWrite = "wb"
                # Save the compressed data to the outputFile.
                with open(outputFile, appendWrite) as openFile2:
                  openFile2.write(data)
              else:
                # Save uncompressed data to the outputFile.
                with open(outputFile, appendWrite) as openFile2:
                  # Decide whether we need to create a new output file or append to an existing one.
                  if os.path.isfile(outputFile):
                    appendWrite = "ab"
                  else:
                    appendWrite = "wb"
                  openFile2.write(data)
              counter0 += 1
          openFile.close()
          openFile2.close()
          # Decide whether we need to create a new output file or append to an existing one.
          if os.path.isfile(dictFile):
            appendWrite = "ab"
          else:
            appendWrite = "wb"
          with open(dictFile, appendWrite) as openFile3:
            openFile3.write(str(dictionary))
            openFile3.close()
      else:
        dictionary = result =  'ERROR'
        data = ''
    else: 
      dictionary = result =  'ERROR'
      data = ''
  if not os.path.isfile(dictFile) or dictionary == 'ERROR' or result == 'ERROR':
    dictionary = result = 'ERROR'
    data = ''
    print ('ERROR!!! xPress173, The operation failed to generate a dictionary for inputFile '+inputFile+'!')
  return dictionary, data, result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function to iterate through the temp file and compress its actual data using the dictionary.
def compressFile(outputFile, compressedData, dictionary):
  print('OP-Act: Writing dictionary to outputFile '+outputFile)
  archive = open(outputFile, "ab")
  archive.write('@!@!@!DICTSTART@!@!@!')
  pickle.dump(dictionary, archive)
  archive.write('@!@!@!DICTEND@!@!@!')
  archive.close()
  result = 1
  if not os.path.isfile(outputFile):
    print('ERROR!!! xPress232, The operation failed to write the dictionary to outputFile'+outputFile)
    result = 'ERROR'
  return result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to extract compressed data and reconstruct the original file.
def extractFile(inputFile, outputFile):
  if os.path.isfile(inputFile):
    print('OP-Act: Extracting inputFile '+inputFile)
    compressedData = open(inputFile, "rb")

    result = re.search('@!@!@!DICTSTART@!@!@!(.*)@!@!@!DICTEND@!@!@!', compressedData)
    print result.group(1)

    result = 1
  else:
    result = 'ERROR'
    print(('ERROR!!! xPress242, The operation failed to extract inputFile '+inputFile+'!'))
  return result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Code to compress a specified file.
if sys.argv[1] == 'c':
  tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath = parseArgs(sys.argv[1:])  
  dictionary, compressedData, dictResult = buildDictionary(outputFile, inputFile, dictFile)
  if dictResult != 'ERROR':
    compressionResult = compressFile(outputFile, compressedData, dictionary)
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
print ("\n")
# --------------------------------------------------