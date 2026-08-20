#!/usr/bin/env python3
"""
Punto de entrada principal para el emulador SAE J1939.
"""

import time
import sys
import can
from models.spn import SPN
from models.pgn import PGN

def init_vcan_interface(channel: str = "vcan0"):
    """Inicializa la interfaz SocketCAN en Linux."""
    try:
        bus = can.interface.Bus(channel=channel, bustype="socketcan")
        return bus
    except OSError:
        print(f"Error: No se pudo conectar a la interfaz '{channel}'.")
        print("Asegúrate de haberla activado en Linux con:")
        print(f"  sudo modprobe vcan")
        print(f"  sudo ip link add dev {channel} type vcan")
        print(f"  sudo ip link set up {channel}")
        sys.exit(1)


def main():
    # 1. Conectar a SocketCAN
    bus = init_vcan_interface("vcan0")

    # 2. Configurar PGN 65265 (Cruise Control / Vehicle Speed)
    ccvs = PGN(
        pgn_number=65265,
        name="Cruise Control/Vehicle Speed",
        priority=6,
        source_address=0x00,
    )

    # 3. Configurar SPN 84 (Vehicle Speed - Bytes 2 y 3)
    spn_speed = SPN(
        spn_id=84,
        name="Vehicle Speed",
        resolution=0.00390625,
        offset=0.0,
        length_bytes=2,
        start_byte=2,
        min_val=0.0,
        max_val=250.0,
    )

    ccvs.add_spn(spn_speed)

    # 4. Transmisión continua a 10 Hz
    simulated_speed = 0.0
    can_id = ccvs.calculate_can_id()

    print(f"--- Emulador J1939 Activo ---")
    print(f"PGN: {ccvs.pgn_number} ({ccvs.name}) | CAN ID: 0x{can_id:08X}")
    print("Transmitiendo en vcan0 (10 Hz). Presiona Ctrl+C para detener.\n")

    try:
        while True:
            # Simular incremento de velocidad (0 a 120 km/h)
            simulated_speed = (simulated_speed + 0.5) % 120.0
            spn_speed.set_value(simulated_speed)

            # Construir payload y emitir
            payload = ccvs.build_message()
            msg = can.Message(
                arbitration_id=can_id,
                data=payload,
                is_extended_id=True,
            )

            bus.send(msg)
            print(
                f"\rTransmitiendo: {simulated_speed:5.1f} km/h | Data: {payload.hex(' ')}",
                end="",
            )

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nEmulación detenida correctamente.")


if __name__ == "__main__":
    main()
