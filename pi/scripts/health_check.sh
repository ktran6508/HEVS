#!/bin/bash
# health_check.sh
# Session startup health check — shows only relevant system status
# Run at the start of every development session

echo "================================"
echo "       HEVS Health Check        "
echo "================================"
echo ""

# Temperature
TEMP=$(vcgencmd measure_temp | cut -d= -f2)
echo "Temperature:     $TEMP"

# Storage
STORAGE=$(df -h | grep mmcblk0p2 | awk '{print $3 " used / " $2 " total (" $5 " full)"}')
echo "Storage:         $STORAGE"

# RAM
RAM=$(free -h | grep Mem | awk '{print $7 " available / " $2 " total"}')
echo "RAM:             $RAM"

echo ""

# Capture card
if v4l2-ctl --list-devices 2>/dev/null | grep -q "Guermok"; then
    echo "Capture Card:    OK (/dev/video0)"
else
    echo "Capture Card:    NOT FOUND — check USB connection"
fi

# Camera PTP
if gphoto2 --auto-detect 2>/dev/null | grep -q "Sony"; then
    echo "Camera (A6000):  OK (PC Remote mode)"
else
    echo "Camera (A6000):  NOT FOUND — check USB + PC Remote mode"
fi

echo ""

# Software versions
GST=$(gst-inspect-1.0 --version 2>/dev/null | head -1)
GPHOTO=$(gphoto2 --version 2>/dev/null | head -1)
echo "GStreamer:       $GST"
echo "gphoto2:         $GPHOTO"

echo ""
echo "================================"

# Overall status
PASS=true

if ! v4l2-ctl --list-devices 2>/dev/null | grep -q "Guermok"; then
    PASS=false
fi
if ! gphoto2 --auto-detect 2>/dev/null | grep -q "Sony"; then
    PASS=false
fi

if [ "$PASS" = true ]; then
    echo " Status: HEALTH CHECK COMPLETE"
else
    echo " Status: CHECK FAILURES ABOVE"
fi

echo "================================"
