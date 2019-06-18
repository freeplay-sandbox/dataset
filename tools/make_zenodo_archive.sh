#! /usr/bin/sh

git archive -o pinsoro.zip --prefix=pinsoro/ HEAD
cd ..
ln -s freeplay_sandbox/ pinsoro
zip -rv freeplay_sandbox/pinsoro.zip pinsoro/data/*/pinsoro-*.csv
zip -rv freeplay_sandbox/pinsoro.zip pinsoro/data/*/*.json
rm pinsoro
cd freeplay_sandbox
