#!/usr/bin/env bash

if $(npm list -g | grep -q "webtorrent"); then
	echo "webtorrent found... SKIPPING install"
else
	
	npm install webtorrent-cli -g
fi
