#!/bin/bash
cd ~/flaskapp
gunicorn --bind 0.0.0.0:5000 server:app
