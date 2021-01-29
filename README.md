# Uni project

### Requirements
+ Python 3.6+ (Recommended 3.8.6)
+ [League of Legends API Key](https://developer.riotgames.com/)



### Running the app:
Program uses [Waitress](https://github.com/Pylons/waitress) for serving wscgi Flask app. To start it, run:
```
$ waitress-serve --port=[PORT NUMBER] server:app
```
Then access app via `localhost:port_number`.