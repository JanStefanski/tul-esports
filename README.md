# Uni project

## Requirements
+ Python 3.6+ (Recommended 3.8.6)
+ [League of Legends API Key](https://developer.riotgames.com/)

## Installation
First you need to download necessary libraries & packages from PyPi, by running command:
```
$ pip install -r requirements.txt
```

Then a convenient setup script should walk you through the process of installation. Start it by running:
```
$ python setup.py
```
Later, if you only need to update your API key you can run:
```
$ python setup.py -ulk [LEAGUE_API_KEY]
```
to simply update it.

## Running the app
Program uses [Waitress](https://github.com/Pylons/waitress) for serving wscgi Flask app. To start it, run:
```
$ waitress-serve --port=[PORT NUMBER] server:app
```
Then access app via `localhost:port_number`.