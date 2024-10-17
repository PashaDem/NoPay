#!/bin/bash
set -e

celery -A nopay worker -l info --uid=nobody --gid=nogroup
