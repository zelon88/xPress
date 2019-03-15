# --------------------------------------------------
# xPress.py
# v1.1 - 3/14/2019

# Justin Grimes (@zelon88)
#   https://github.com/zelon88/xPress
#   https://www.HonestRepair.net

# Made on Windows 7 with Python 2.7.12

# This program is a file compressor and extractor that uses
# a new compression algorithm designed and dictated by this 
# document. It has an adjustable dictionary value length and
# can decompress files without special extractor preparations.

# Code blocks are prefaced with COMPRESS or EXTRACT to denote
# which function they support, for easier code surfing.
# --------------------------------------------------

# --------------------------------------------------
# VALID ARGUMENTS / PARAMETERS / SWITCHES
# If you combine multiple verbosity or log levels the last specified will be used.

#  h - Display help text. 1st argument.
#  c - Convert. 1st argument.
#  e - Extract. 1st argument.

#  <C:\Path\To\Input_File> - 2nd argument.

#  <C:\Path\To\Output_File> - 3rd argument

#  v0 - Verbosity 0. Optional. Disable output. 4th or 5th argument.
#  v1 - Verbosity 1. Optional. Only errors are output. 4th or 5th argument.
#  v2 - Verbosity 2. Optional. Everything is output. 4th or 5th argument.

#  l0 - Log level 0. Optional. Disable logging. 4th or 5th argument.
#  l1 - Log level 1. Optional. Only errors logged. 4th or 5th argument. 
#  l2 - Log level 2. Optional. Everything is logged. 4th or 5th argument.
# --------------------------------------------------

# --------------------------------------------------
# EXAMPLE COMMANDS
# xPress.py h
# xPress.py c c:\TestFolder\test.png c:\TestFolder\output.xpr
# xPress.py c c:\TestFolder\test.png c:\TestFolder\test.xpr v1 l1
# xPress.py e c:\TestFolder\test.xpr c:\TestFolder\test.png v0 l3
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Load required modules and set global variables.
import sys, getopt, datetime, os, psutil, math, pickle, re
now = datetime.datetime.now()
time = now.strftime("%B %d, %Y, %H:%M")
logging = 1
verbosity = 2
error = feature = inputFile = inputPath = dictPath = entryPrefix = \
dictFile = tempPath = tempFile = outputPath = outputFile = ''
currentPath = os.path.dirname(__file__)
logFile = os.path.join(currentPath, 'xPress.log')
chunkSize = offset = chunkCount = errorCounter = 0
dictLength = 12
dictionaryPrefix = '@!@!DST@!@!'
dictionarySufix = '@!@!DND@!@!'
logPrefix = 'OP-Act: '
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# A function to print output to the console in a consistent manner.
def printGracefully(logPrefix, message):
  print (logPrefix+message+'.')
  return 1
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# A function to kill the program gracefully during unrecoverable error.
# The errorMessage will be displayed to the user, unless the s switch is set.
# Note this uses sys.exit(), which not only kills this script but the entire interpreter.
def dieGracefully(errorMessage, errorNumber, errorCounter):
  print ('ERROR-'+str(errorCounter)+'!!! xPress'+str(errorNumber)+': '+str(errorMessage)+' on '+str(time)+'!')
  sys.exit()
  return 1
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# A function to write an entry to the logFile. 
# Do not punctuate your log entries with punctuation, or it will look strange.
# Set the errorNumber to 0 for regular prefix (default is "OP-Act").
# If the entry is an error message, set errorNumber to an int greater than 0.
def writeLog(logFile, logEntry, time, errorNumber, errorCounter):
  if os.path.isfile(logFile):
    append = "ab"
  else:
    append = "wb"
  if errorNumber > 0:
    entryPrefix = 'ERROR-'+str(errorCounter)+'!!! xPress'+str(errorNumber)+': '
  else: 
    entryPrefix = logPrefix
  entrySufix = ' on '+str(time)+'.'
  with open(logFile, append) as logData:
    logData.write(entryPrefix+logEntry+entrySufix+"\n")
    logData.close
  return 1
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Process user supplied arguments/parameters/switches.
def parseArgs(logging, verbosity, argv, errorCounter):
  # Check if any arguments were passed.
  try:
    opts, args = getopt.getopt(argv,"h")
  except getopt.GetoptError:
    # Print the help text if the "h" argument is passed
    print ('xPress.py <c>or<e> <inputFile> <outputFile>')
    sys.exit(2)
  if sys.argv[1] == 'c':
    feature = 'compress'
  if sys.argv[1] == 'e':
    feature = 'extract'
  if len(sys.argv) > 4:
    # Set the logging level from argument 4.
    if sys.argv[4] == 'l0':
      logging = 0
    if sys.argv[4] == 'l1':
      logging = 1
    if sys.argv[4] == 'l2':
      logging = 2
    # Set the verbosity level from argument 4.
    if sys.argv[4] == 'v0':
      verbosity = 0
    if sys.argv[4] == 'v1':
      verbosity = 1
    if sys.argv[4] == 'v2':
      verbosity = 2
  if len(sys.argv) > 5:
    # Set the logging level from argument 5.
    if sys.argv[5] == 'l0':
      logging = 0
    if sys.argv[5] == 'l1':
      logging = 1
    if sys.argv[5] == 'l2':
      logging = 2
    # Set the verbosity level from argument 5.
    if sys.argv[5] == 'v0':
      verbosity = 0
    if sys.argv[5] == 'v1':
      verbosity = 1
    if sys.argv[5] == 'v2':
      verbosity = 2
  # Check to see if an input file argument was supplied.
  try:
    sys.argv[1]
  except IndexError:
    # Display an error and stop execution if the input argument is missing.
    # "ERROR-<#>!!! xPress89, No input file was specified on <time>."
    errorCounter += 1    
    message = 'No input file was specified'
    if logging > 0:
      writeLog(logFile, message, time, 89, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 89, errorCounter)
    else:
      sys.exit()
  else:
    inputFile = sys.argv[2]
    inputPath = os.path.dirname(inputFile)
    # Display an error and stop execution if the input file does not exist.
    if not os.path.exists(inputFile):
      # "ERROR-<#>!!! xPress97, The input file specified does not exist on <time>."
      errorCounter += 1
      message = 'The input file specified does not exist'
      if logging > 0:
        writeLog(logFile, message, time, 97, errorCounter)
      if verbosity > 0:
        dieGracefully(message, 97, errorCounter)
      else:
        sys.exit()  
  # Check to see if an output file argument was supplied.
  try:
    sys.argv[3]
  except IndexError:
    # Display an error and stop execution if the output argument is missing. 
    # "ERROR-<#>!!! xPress108, No output file was specified on <time>."
    errorCounter += 1
    message = 'No output file was specified'
    if logging > 0:
      writeLog(logFile, message, time, 108, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 108, errorCounter)
    else:
      sys.exit()
  else: 
    outputFile = sys.argv[3]
    outputPath = os.path.dirname(outputFile)
    tempFile = sys.argv[3]+'-TEMP.dat'
    tempPath = os.path.dirname(tempFile)
    dictFile = sys.argv[3]+'-DICT.dat'
    dictPath = os.path.dirname(dictFile)
    # Check to see that a directory exists to put an output file into and display an error if not.
    if not os.path.exists(outputPath):
      # "ERROR-<#>!!! xPress108, The output file specified relies on an invalid directory on <time>."
      errorCounter += 1
      message = 'The output file specified relies on an invalid directory'
      if logging > 0:
        writeLog(logFile, message, time, 126, errorCounter)
      if verbosity > 0:
        dieGracefully(message, 126, errorCounter)
      else:
        sys.exit()
  return logging, verbosity, tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Define the chunkSize based on fileSize and available memory.
# We need to store 2 copies of the offset buffer and the rest of this application.
# By dynamically setting how much of a file to load into memory at a time, xPress should be hardware agnostic.
# Severely limited machines with memory levels measured in hundreds of megabytes may see less compression performance than machines with more memory.
def defineChunkSize(logging, verbosity, inputFile):
  chunkSize = 0
  # Get the filesize of the input file.
  message = 'Defining chunkSize with inputFile '+str(inputFile)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  fileSize = int(os.path.getsize(inputFile))
  # Get the available memory.
  mem = psutil.virtual_memory()
  availableMemory = mem.available
  message = 'Available memory is '+str(availableMemory)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  # Our chunkSize is 1/4 of available memory. This translates to about 1/2 of available memory used once we load each chunk twice.
  chunkSize = int(availableMemory) / 2
  # If the chunkSize is smaller than the file being processed the entire file becomes the only chunk.
  if chunkSize >= fileSize:
    chunkSize = fileSize
  message = 'ChunkSize is '+str(chunkSize)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  return chunkSize
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Define what the file offsets and number of chunks based on fileSize and chunkSize.
# If a file is too big it is divided into small chunks.
# The offset is different from the chunkSize in that it is evenly divisible by the filesize.
# To put it differently, the chunkSize limits global memory usage and the offset allocates an exact quantity of memory for each operation.
def defineOffset(logging, verbosity, inputFile, chunkSize):
  offset = chunkCount = result = 'ERROR'
  # Verify that the inputFile exists.
  if os.path.isfile(inputFile):
    # Get the filesize of the input file.
    fileSize = int(os.path.getsize(inputFile))
    chunkSize = int(chunkSize)
    message = 'Defining offset with chunkSize of '+str(chunkSize)
    if logging > 1:
      writeLog(logFile, message, time, 0, 0)
    if verbosity > 1:
      printGracefully(logPrefix, message)
    # Decide if the file should be chunked or processed as a whole.
    if fileSize > chunkSize:
      chunkCount = int(math.ceil(fileSize / chunkSize))
      offset = fileSize
    else:
      chunkCount = 1
    offset = fileSize / chunkCount
    result = 1
    message = 'Offset is '+str(offset)+', chunkCount is '+str(chunkCount)
    if logging > 1:
      writeLog(logFile, message, time, 0, 0)
    if verbosity > 1:
      printGracefully(logPrefix, message)
  else:
    offset = chunkCount = result = 'ERROR'
    chunkCount = 0
  if offset > sys.maxint:
    offset = sys.maxint;
    offset / 10
  return offset, chunkCount, result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function for determining a dictLength for the operation.
def defineDictLength(inputFile):
  message = 'Defining dictLength with inputFile '+str(inputFile)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  # Get the filesize of an inputFile for hueristics.
  size = os.stat(inputFile)
  size = size.st_size
  if size < 10:
    dictLength = int(size - (0.5 * size))
    threshold = 0.005
  if size > 10:
    dictLength = int(size - (0.99 * size))
    threshold = 10
  if size > 100:
    dictLength = int(size - (0.99 * size))
    threshold = 10
  if size > 1000:
    dictLength = int(size - (0.99 * size))
    threshold = 1
  if size > 10000:
    dictLength = int(size - (0.99 * size))
    threshold = 0.01
  if size > 100000:
    dictLength = int(size - (0.99 * size))
    threshold = 0.001
  if size > 250000:
    dictLength = int(size - (0.99 * size))
    threshold = .005
  if size > 500000:
    dictLength = int(size - (0.999 * size))
    threshold = .000005
  if size > 1000000:
    dictLength = int(size - (0.99999 * size))
    threshold = 0.000001 
  if size > 10000000:
    dictLength = int(size - (0.999999 * size))
    threshold = 0.0000001
  if size > 100000000:
    dictLength = int(size - (0.9999999 * size))
    threshold = 0.0001
  # Set a default minimum.
  if dictLength < 2:
    dictLength = 2
  message = 'DictLength is ' + str(dictLength)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  return dictLength, threshold
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function to iterate through the temp file and build a dictionary for the file.
def buildDictionary(logging, verbosity, outputFile, inputFile, dictFile, dictLength, threshold, dictionaryPrefix, dictionarySufix, errorCounter):
  dictionary = result = data = 'ERROR'
  skip = skipped = False
  # Verify that no output file or dict file exists already.
  if os.path.isfile(outputFile) or os.path.isfile(dictFile):
    errorCounter += 1
    message = 'The output file or temp files already exist for outputFile '+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 280, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 280, errorCounter)
    else:
      sys.exit()
  else:
    # Verify that in input file exists.
    if os.path.isfile(inputFile):
      result = 1
      adjusted = 0
      message = 'Building a dictonary with inputFile '+str(inputFile)
      if logging > 1:
        writeLog(logFile, message, time, 0, 0)
      if verbosity > 1:
        printGracefully(logPrefix, message)
      # Set some variables.
      dictionary = {}
      dictIndexNumber = counter0 = dictCount = lastDictLen = lastChunk = 0
      dictIndex = '#',str(dictIndexNumber),'$'
      tempChunkSize = defineChunkSize(logging, verbosity, inputFile)
      tempOffset, tempChunkCount, dOffResult = defineOffset(logging, verbosity, inputFile, tempChunkSize)
      if dOffResult != 'ERROR' and tempOffset != 'ERROR' and tempChunkCount > 0:
        # Open the input file.
        with open(inputFile, "rb") as openFile:
          # Stop execution after all chunks are processed.
          while counter0 <= tempChunkCount:
            newLoop = True
            # Set the current offset.
            filePosition = openFile.tell()
            # Fill up the offset buffer.
            data = openFile.read(tempOffset)
            dataLen = lastDataLen = len(data)
            dictionaryLen = lastDictLen = len(dictionary)
            # Select some data and attempt to compress it.
            # dictLength can only be set before the first loop for this logic.
            # Any changes to dictLength made during this loop DO NOT change this "for."
            for i in xrange(0, len(data), dictLength):
              message = 'Initiating a compression loop. Byte '+str(i)+' of '+str(dataLen)+' in chunk '+str(counter0)
              if logging > 1:
                writeLog(logFile, message, time, 0, 0)
              if verbosity > 1:
                printGracefully(logPrefix, message)
              # Fill up the chars buffer.
              chars = data[i:(i+dictLength)]
              dataLen = len(data)
              dataMatch = data.count(chars)
              # Calculate the percentageOf compression achieved in the last loop.
              percentageOf = ((lastDataLen - dataLen) * lastDataLen) / 100
              # Check to see that the threshold is being met.
              if (dataMatch >= 2 and (newLoop == True or dataLen <= lastDataLen)):
                dictIndexNumber += 1
                dictIndex = '#'+str(dictIndexNumber)+'$'
                lastDataLen = len(data)
                data = data.replace(chars, dictIndex)
                dataLen = len(data)
                lastDictLen = len(dictionary)
                dictionary.update({dictIndex : chars})
                dictionaryLen = len(dictionary)
                dictCount += 1
                percentageOf = ((lastDataLen - dataLen) / lastDataLen) * 100
                # Save the compressed data to the output file.
                if newLoop == True and lastChunk != counter0:
                  append0 = "ab"
                else:
                  append0 = "wb"
                with open(outputFile, append0) as openFile2:
                  openFile2.write(data)
                  openFile2.close()
                newLoop = False
              else:
                # Decrease the dictLengh if results are not forthcoming.
                if adjusted < 4 and dictLength != 3:
                  dictLength = dictLength / 2
                  if dictLength > int(len(data) / 2):
                    dictLength = dictLength / (dictLength / 2)
                  message = 'Decreasing the dictLength, currently ' + str(dictLength)
                  if logging > 1:
                    writeLog(logFile, message, time, 0, 0)
                  if verbosity > 1:
                    printGracefully(logPrefix, message)
                  adjusted += 1
                  with open(outputFile, "wb") as openFile2:
                    openFile2.write(data)
                    openFile2.close()
                  continue
                # Increase the dictLengh if results are not forthcoming.
                if adjusted >= 4 and adjusted < 9:
                  dictLength = dictLength * dictLength
                  if dictLength > int(len(data) / 2):
                    dictLength = dictLength / (dictLength / 2)
                  message = 'Increasing the dictLength, currently ' + str(dictLength)
                  if logging > 1:
                    writeLog(logFile, message, time, 0, 0)
                  if verbosity > 1:
                    printGracefully(logPrefix, message)
                  adjusted += 1
                  with open(outputFile, "wb") as openFile2:
                    openFile2.write(data)
                    openFile2.close()
                  continue
                  newLoop = False
                # Save uncompressed data to the output file.
                message = 'Skipping bytes '+str(i)+' of '+str(dataLen)+' in chunk '+str(counter0)
                if logging > 1:
                  writeLog(logFile, message, time, 0, 0)
                if verbosity > 1:
                  printGracefully(logPrefix, message)
                with open(outputFile, "wb") as openFile2:
                  openFile2.write(data)
                  openFile2.close()
                break
              newLoop = False
              lastChunk = counter0            
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
    errorCounter += 1
    message = 'The operation failed to generate a dictionary for inputFile '+str(inputFile)
    if logging > 0:
      writeLog(logFile, message, time, 346, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 346, errorCounter)
    else:
      sys.exit()
  else:
    message = 'Writing a temporary dictFile to '+str(dictFile)
    if logging > 1:
      writeLog(logFile, message, time, 0, 0)
    if verbosity > 1:
      printGracefully(logPrefix, message)
  return dictionary, data, result
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# A function to iterate through the temp file and compress its actual data using the dictionary.
def compressFile(logging, verbosity, outputFile, compressedData, dictionary, dictionaryPrefix, dictionarySufix, errorCounter):
  message = 'Writing dictionary data to outputFile '+str(outputFile)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  archive = open(outputFile, "ab")
  archive.write(dictionaryPrefix)
  pickle.dump(dictionary, archive)
  archive.write(dictionarySufix)
  archive.close()
  result = 1
  # Verify that an output file was created.
  if not os.path.isfile(outputFile):
    result = 'ERROR'
    errorCounter += 1
    message = 'There was an error writing the dictionary to the outputFile '+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 373, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 373, errorCounter)
    else:
      sys.exit()
  return result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to extract compressed data and reconstruct the dictionary file.
def extractDictionary(logging, verbosity, inputFile, outputFile, dictFile, dictionaryPrefix, dictionarySufix, errorCounter):
  result = dictionary = inData = outputRaw = 'ERROR'
  # Perform sanity checks before attempting anything.
  if os.path.isfile(outputFile) or os.path.isfile(dictFile):
    message = 'The output file or temp files already exist for outputFile '+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 390, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 390, errorCounter)
    else:
      sys.exit()
  else:
    if os.path.isfile(inputFile):
      message = 'Extracting dictionary from inputFile '+str(inputFile)
      if logging > 1:
        writeLog(logFile, message, time, 0, 0)
      if verbosity > 1:
        printGracefully(logPrefix, message)
      # Open the input file and put its contents into memory.
      with open(inputFile, "rb") as inputData:
        inData = inputData.read()
        inputData.close()
      # Extract the dictionary data from the input data.
      dictionaryData = inData[inData.find(dictionaryPrefix)+len(dictionaryPrefix):inData.find(dictionarySufix)].replace(dictionaryPrefix, '').replace(dictionarySufix, '')
      # Write the extracted dictionary data to a temporary dictionary file.
      with open(dictFile, "wb") as dictData:
        dictData.write(dictionaryData)
        dictData.close()
        # Create an output file, separate compressed data from dictionary data, and put just the compressed data into it.
      with open(outputFile, "wb") as outputData:
        outputRaw = inData.replace(dictionaryPrefix+dictionaryData+dictionarySufix, '')
        inData = ''
        outputData.write(outputRaw)
        outputData.close()
      dictionaryData = ''
      dictFileOpen = open(dictFile, "rb")
      dictionary = pickle.load(dictFileOpen)
      dictFileOpen.close()
      result = 1
    else:
      result = dictionary = outputRaw = 'ERROR'
      errorCounter += 1
      message = 'The operation failed to extract a dictionary from inputFile '+str(inputFile)
      if logging > 0:
        writeLog(logFile, message, time, 428, errorCounter)
      if verbosity > 0:
        dieGracefully(message, 428, errorCounter)
      else:
        sys.exit()
  if not os.path.isfile(dictFile):
    result = dictionary = outputRaw = 'ERROR'
    errorCounter += 1
    message = 'The operation failed to write the dictionary to outputFile'+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 438, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 438, errorCounter)
    else:
      sys.exit()
  return dictionary, outputRaw, result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to loop through the dictionary and compressed data and look for matches.
def dictionaryLoop(logging, verbosity, compressedData, dictionary, errorCounter):
  result = 'ERROR'
  matchCount = 0
  if not isinstance(dictionary, dict):
    errorCounter += 1
    message = 'The supplied dictionary is not readable'
    if logging > 0:
      writeLog(logFile, message, time, 455, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 455, errorCounter)
    else:
      sys.exit()
  else:
    result = 1
    message = 'Initiating a decompression loop'
    if logging > 1:
      writeLog(logFile, message, time, 0, 0)
    if verbosity > 1:
      printGracefully(logPrefix, message)
    # Loop through each key in the dictionary, count and replace matches.
    for key, value in dictionary.iteritems():
      matchCount = matchCount + compressedData.count(key)
      compressedData = compressedData.replace(key, value)
      message = 'Decompressing '+str(matchCount)+' matches'
      if logging > 1:
        writeLog(logFile, message, time, 0, 0)
      if verbosity > 1:
        printGracefully(logPrefix, message)
  return compressedData, dictionary, matchCount, result
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# A function to decompress an input file.
def decompressFile(logging, verbosity, outputFile, compressedData, dictionary, errorCounter):
  result = 'ERROR'
  counter = 1
  if not os.path.isfile(outputFile) or compressedData == 'ERROR' or dictionary == 'ERROR':
    errorCounter += 1
    message = 'Could not decompress outputFile '+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 482, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 482, errorCounter)
    else:
      sys.exit()
  else:
    result = 1
    message = 'Initiating decompressor on inputFile '+str(inputFile)
    if logging > 1:
      writeLog(logFile, message, time, 0, 0)
    if verbosity > 1:
      printGracefully(logPrefix, message)
    # Loop through the file and look for dictionary matches.
    while counter != 0:
      compressedData, dictionary, counter, result = dictionaryLoop(logging, verbosity, compressedData, dictionary, errorCounter)
      if result == 'ERROR' or compressedData == 'ERROR':
        errorCounter += 1
        message = 'The operation failed during decompression of outputFile '+str(outputFile)
        if logging > 0:
          writeLog(logFile, message, time, 500, errorCounter)
        if verbosity > 0:
          dieGracefully(message, 500, errorCounter)
        else:
          sys.exit()
    with open(outputFile, "wb") as outputData:
      outputData.write(compressedData)
      outputData.close()
      compressedData = ''
    if not os.path.isfile(outputFile):
      result = 'ERROR'
      errorCounter += 1
      message = 'The operation failed to create an outputFile '+str(outputFile)
      if logging > 0:
        writeLog(logFile, message, time, 512, errorCounter)
      if verbosity > 0:
        dieGracefully(message, 512, errorCounter)
      else:
        sys.exit()
    else:
      result = 1
  return result 
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
# Display some text to kick things off.
def printWelcome(logging, verbosity):
  message = 'Starting xPress Compress on '+str(time)
  if logging > 1:
    writeLog(logFile, message, time, 0, 0)
  if verbosity > 1:
    printGracefully(logPrefix, message)
  return 1
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS
# Code to compress a specified file.
if sys.argv[1] == 'c':
  logging, verbosity, tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath = parseArgs(logging, verbosity, sys.argv[1:], errorCounter)  
  printWelcome(logging, verbosity)
  dictLength, threshold = defineDictLength(inputFile)
  dictionary, compressedData, dictResult = buildDictionary(logging, verbosity, outputFile, inputFile, dictFile, dictLength, threshold, dictionaryPrefix, dictionarySufix, errorCounter)
  if dictResult != 'ERROR':
    compressionResult = compressFile(logging, verbosity, outputFile, compressedData, dictionary, dictionaryPrefix, dictionarySufix, errorCounter)
  else:
    errorCounter += 1
    message = 'The operation failed to create an outputFile '+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 664, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 664, errorCounter)
    else:
      sys.exit()
# --------------------------------------------------

# --------------------------------------------------
# EXTRACT
# Code to extract a specified file.
if sys.argv[1] == 'e':
  logging, verbosity, tempFile, tempPath, inputFile, inputPath, outputFile, outputPath, dictFile, dictPath = parseArgs(logging, verbosity, sys.argv[1:], errorCounter)  
  printWelcome(logging, verbosity)
  dictionary, compressedData, dictResult = extractDictionary(logging, verbosity, inputFile, outputFile, dictFile, dictionaryPrefix, dictionarySufix, errorCounter)
  if dictResult != 'ERROR':
    decompressionResult = decompressFile(logging, verbosity, outputFile, compressedData, dictionary, errorCounter)
  else:
    errorCounter += 1
    message = 'The operation failed to create an outputFile '+str(outputFile)
    if logging > 0:
      writeLog(logFile, message, time, 683, errorCounter)
    if verbosity > 0:
      dieGracefully(message, 683, errorCounter)
    else:
      sys.exit()
# --------------------------------------------------

# --------------------------------------------------
# COMPRESS & EXTRACT
message = 'Operation complete'
if logging > 1:
  writeLog(logFile, message, time, 0, 0)
if verbosity > 1:
  printGracefully('', message)
  print("\n")
# --------------------------------------------------