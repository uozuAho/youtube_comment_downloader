# Youtube comment downloader

https://developers.google.com/youtube/v3/quickstart/python

# quick start
Create a google dev API key that can access youtube. Save the key to a file in
this dir called '.secrets':

```
apiKey=YOUR API KEY HERE
```

Install python 3.8+. Then:

```sh
python -m venv .venv
. .venv/Scripts/activate
python dl.py > SOME_FILENAME
```

# creating standalone exe
Run `./create_exe.sh`, then have a look in dist/dl
Use the bat file to run it.
