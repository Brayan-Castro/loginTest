# Login Test

A simple login / register project utilizing PyMySql, Docker-Compose.

## Features
- Dockerized environment
- MySQL + Python (PyMySQL)
- Easy setup with docker-compose
- Hashlib for password encryption

## Changelog

- Removed option to add recovery email to the account (it was useless);
- Modularized the code;
- Removed various instances of code reuse;
- Added consistent 'error codes';
- Changed verification code generation method from random.randrange to secrets.randbelow;
- Changed account password encryption method from Sha256 to bcrypt with salt;
- Added type annotations;

## Planned Changes

- 'Token' to effectively log-in a user;
- Add a second table to the database with dummy data to simulate users with independent data;
- 'Cookie' to keep user logged in from the start;
- Reformulate some parts of the code (mainly the main() function);
- Improve error handling;