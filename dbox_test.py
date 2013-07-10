# Include the Dropbox SDK libraries
from dropbox import client, rest, session
import sys
import os

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'kx01dqc34x2k3ys'
APP_SECRET = 'bloxfy4mgqc17xy'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
TOKEN_FILE = '/Users/aweber/.secret'
SYNC_DIR = '/Users/aweber/Docs'
SYNC_DIR_LIST = {}
#Take last path to create this folder on your Dropbox folder
DEST_DIR = os.path.split(SYNC_DIR)[1]
  

sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)


try:
    token_file = open(TOKEN_FILE,'r')

except IOError:
    # This is only really needed first time you run the code, create a new token and save it in the secret file!    
    request_token = sess.obtain_request_token()
    # Make the user sign in and authorize this token
    url = sess.build_authorize_url(request_token)#
    print "url:", url
    print "Please authorize in the browser. After you're done, press enter."
    raw_input()
    # Next line will fail if the user didn't visit the above URL and hit 'Allow'
    access_token = sess.obtain_access_token(request_token)
#    # Save the newly created token into a file for further use
    token_file = open(TOKEN_FILE,'w')
    token_file.write("%s|%s" % (access_token.key,access_token.secret) )
    # Really close the file once finished
finally:
    token_file.close()


token_file = open(TOKEN_FILE)
#retrieve token/secret from file and save in our Dropbox session Object
token,key = token_file.read().split('|')
token_file.close()

sess.set_token(token,key)

#Initialise the client with our session object
client = client.DropboxClient(sess)

# Show account information...method returns a dictionary, store that for further tests -- Not needed for now
#Client_info = client.account_info()



#Now create a dictionary containing the file name, and it's size
if os.path.lexists(SYNC_DIR):    
    for file in os.listdir(SYNC_DIR):
        SYNC_DIR_LIST[file] = os.path.getsize(SYNC_DIR + '/' + file)


#Get the same from your dropbox

if DEST_DIR in client.metadata('/')['contents'][0]['path']:
    SYNC_DIR_META = client.metadata(DEST_DIR)
    print 'Destination directory already exists'
else:
    client.file_create_folder(DEST_DIR)
    SYNC_DIR_META = client.metadata(DEST_DIR)
    print 'Just created the destination directory'
    
SYNC_DIR_META_LIST = {}

for file in SYNC_DIR_META['contents']:
    SYNC_DIR_META_LIST[os.path.split(file['path'])[1]] = file['bytes']

#Copy only if file does not exist on Dropbox, or size different from source(modified file) or does not start with . (hidden files)
for file in SYNC_DIR_LIST:
    if (file[0] != '.'):
        if (file not in SYNC_DIR_META_LIST):
            client.put_file(DEST_DIR + '/' + file,open(SYNC_DIR + '/' + file))
            print 'Copying ' + file + ' to Dropbox'
        if  (file in SYNC_DIR_META_LIST) and (SYNC_DIR_META_LIST[file] != SYNC_DIR_LIST[file]):
            client.file_delete(DEST_DIR + '/' + file)
            client.put_file(DEST_DIR + '/' + file,open(SYNC_DIR + '/' + file))
            print 'Updating ' + file + ' to Dropbox'
        
        
print 'Finished copying'    
    

