# Peka-Ai

A small web service to generate a pekachuka presentation from a given input of slides names

## tldr
```
cp config.tpl.json config.json
docker-compose up -d
# open http://localhost:8080
```

## Running the tests
```
python -m unittest discover ./
```

## Development
To ease development the app code can be mounted live in the `docker-compose.yml`:
```
  peka-ai:
    volumes:
      - ./:/app/
```

### Linting
please follow pycodestyle for possible contributions

### Licensing
Open source GPL, See LICENSE.

## Contribution
* [Erignoux Laurent](lerignoux@gmail.com)
