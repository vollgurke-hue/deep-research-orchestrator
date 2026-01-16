#!/bin/bash
# Script um Kernel 6.12.57 als Standard zu setzen

echo "Setze Kernel 6.12.57 als Standard..."

# Variante 1: Mit grub-set-default (einfacher - nutzt Index)
sudo grub-set-default "1>2"

# Update GRUB
sudo update-grub

echo ""
echo "✓ Fertig! Kernel 6.12.57 ist jetzt der Standard-Boot-Eintrag."
echo ""
echo "Du kannst jetzt neu starten und es sollte automatisch der richtige Kernel laden."
echo "Zum Testen: 'sudo reboot'"
