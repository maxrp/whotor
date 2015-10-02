#!/bin/sh

wget --reject "index.html*" --mirror --cut-dirs=3 -np -l1 https://collector.torproject.org/archive/relay-descriptors/server-descriptors/
