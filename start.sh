#!/bin/bash
rm result.txt
rm -r generated-embeddings
rm -r aligned-images
./util/align-dlib.py ./training-images/ align outerEyesAndNose ./aligned-images/ --size 96
./batch-represent/main.lua -outDir ./generated-embeddings/ -data ./aligned-images/
./demos/classifier.py train ./generated-embeddings/

