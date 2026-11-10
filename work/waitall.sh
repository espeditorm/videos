#!/bin/bash
cd /home/user/videos/work
until [ "$(grep -l done chunks/log_*.txt 2>/dev/null | wc -l)" = 3 ]; do
  if grep -q -i "error" chunks/log_*.txt; then echo FAIL; grep -i error chunks/log_*.txt; exit 1; fi
  sleep 20; done
./finalize.sh
