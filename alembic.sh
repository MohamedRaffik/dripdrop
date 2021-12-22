#!/bin/bash

source venv/bin/activate
dotenv -f .env run alembic "$@"
deactivate