CLIENT_ID = "e638c40cd1a44409b42af8f8c393411e"
CLIENT_SECRET = "f5a6a3218c7a49b086ec899592c9ec7c"

#we set our own redirect_uri. This is where spotify sends us all the responses
# If you look at path, "redirect" makes us go to spotify_Callback
#so we set our redirect_uri to "redirect"
REDIRECT_URI = "http://127.0.0.1:8000/spotify/redirect"