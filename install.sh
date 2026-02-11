#!/bin/bash

# Sprawdzenie czy użytkownik ma uprawnienia roota
if [ "$EUID" -ne 0 ]; then 
  echo "Proszę uruchom skrypt jako root (sudo ./install.sh)"
  exit
fi

echo "--- Rozpoczynam instalację Systemu Monitorowania Integralności ---"

# 1. Instalacja zależności
apt update && apt install -y python3-pip
pip3 install watchdog --break-system-packages

# 2. Ustawienie ścieżek
INSTALL_DIR="/opt/my_monitor"
mkdir -p $INSTALL_DIR/backups $INSTALL_DIR/target_dir $INSTALL_DIR/logs

# 3. Kopiowanie plików źródłowych
cp src/*.py $INSTALL_DIR/

# 4. Tworzenie pliku usługi Systemd
cat <<EOF > /etc/systemd/system/file-monitor.service
[Unit]
Description=Monitor Integralnosci Plikow SO2
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 5. Przeładowanie systemd i start usługi
systemctl daemon-reload
systemctl enable file-monitor
systemctl start file-monitor

echo "--- Instalacja zakończona! ---"
echo "Status usługi: $(systemctl is-active file-monitor)"
