# BasicFileTransferServer
<b>Why would I use this?</b>:
Sometimes you don't have access to a USB and don't want to upload the files to github/dropbox/whatever.
And you shouldn't have to. They are your files.

The solution is to transfer files over your local network. You can do this with Python. 


<b>How do I use this?</b>:

  server.py
  
  ```python python server.py -host [HOST?] -port [PORT?] [--log DEBUG|INFO|WARNING|ERROR|CRITICAL]```
  
  
  client.py
  
  ```python python client.py -addr [ADDR?] -port [PORT?] -size [SIZE?] [--log DEBUG|INFO|WARNING|ERROR|CRITICAL] requested_file >> OUTFILE```
  
1. Start the server. The most basic way to do this is by going to the command prompt and typing ```python python server.py```. This will connect to your local network and listen on port 5000 
2. Start the client script. The most basic way to do this is by going to the command prompt and typing ```python python client.py FILE_OR_FOLDER >> OUTFILE```. This will request the specified file whatever machine running server.py and dump it into a file named OUTFILE
3. If you requested a folder, untar it (```bash tar -xvf OUTFILE``` should do the trick) once the request is complete

*Note - you might need to temporarily disable your computer's network firewall on the machine running server.py to transfer your files.
 On windows, you can do this through the Control Panel. You shouldn't have to do anything on the client machine*


<b>Why doesn't this have more features</b>:
The aim of this project is to provide a basic implementation of an async file transfer server.

I use the command line a lot, so both client.py and server.py are set up for command line usage.

I plan on using this project primarily for transferring files on my local network. 
Currently, server.py allows for transmission of an individual file to the client (similar
to an HTTP GET request). If the file happens to be a directory, it is sent over the
network as a tarball. I assume that the client machine has python's tarfile module or something
similar that can be used to decipher the tarball.

I'm sure there are more fully-featured programs in the wild. If you see one with a cool feature
that could make sense in this project, let me know and I will try to add it.
