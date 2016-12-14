#!/usr/bin/env sh

usb_path='/run/media/of-1/86B3-7AD4/lecroyWaverunner/'

rsync -rvhz "$usb_path" .
