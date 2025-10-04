#!/bin/bash

r=100
while ! nextpnr-ecp5 $* > nextpnr.log 2>& 1
do
  ((--r)) || exit 2
  grep "Max frequency.*clk" nextpnr.log | tail -1
done

exit 0
