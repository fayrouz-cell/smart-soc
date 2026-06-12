@echo off
REM Script to run IDS locally in replay mode (Windows)

echo Starting IDS in replay mode...
python main.py --start --mode replay --pcap data\pcap_samples\sample_traffic.pcap


