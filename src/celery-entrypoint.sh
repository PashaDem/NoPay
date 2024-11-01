#!/bin/bash
celery -A nopay worker -l info --uid=nobody --gid=nogroup
