#!/usr/bin/env python3
"""
Punto de entrada principal para el emulador SAE J1939.
"""

import time
import sys
import can
import json
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


def load_catalog(filepath: str) -> list[PGN]:
    """Lee un catálogo JSON e instancia la lista de objetos PGN con sus SPNs."""
    with open(filepath, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)

    pgn_objects = []

    for pgn_key, pgn_info in catalog_data.items():
        # Instanciar el PGN
        pgn_obj = PGN(
            pgn_number=int(pgn_key),
            name=pgn_info["name"],
            priority=pgn_info.get("priority", 6),
            source_address=pgn_info.get("source", 0x00),
        )

        # Instanciar cada SPN y agregarlo al PGN
        for spn_info in pgn_info.get("spns", []):
            spn_obj = SPN(
                spn_id=spn_info["id"],
                name=spn_info["name"],
                resolution=spn_info["resolution"],
                offset=spn_info["offset"],
                length_bytes=spn_info["length_bytes"],
                start_byte=spn_info["start_byte"],
                min_val=spn_info["min_val"],
                max_val=spn_info["max_val"],
            )
            # Asignar el valor por defecto si existe
            if "default" in spn_info:
                spn_obj.set_value(spn_info["default"])

            pgn_obj.add_spn(spn_obj)

        pgn_objects.append(pgn_obj)

    return pgn_objects


def main():
    # 1. Conectar a SocketCAN
    bus = init_vcan_interface("vcan0")
    # 1.1 Cargar tramas desde archivo json:
    lista_tramas = load_catalog("core/catalog.json")
    print(
        f"--- Emulador J1939 Activo ({len(lista_tramas)} PGNs cargados) ---"
    )
    for pgn in lista_tramas:
        print(
            f"  - PGN {pgn.pgn_number} ({pgn.name}) | CAN ID: 0x{pgn.calculate_can_id():08X}"
        )
    # 2. Configurar PGN 65265 (Cruise Control / Vehicle Speed)
    # 3. Ciclo de emisión
    try:
        while True:
            for pgn in lista_tramas:
                can_id = pgn.calculate_can_id()
                payload = pgn.build_message()

                msg = can.Message(
                    arbitration_id=can_id,
                    data=payload,
                    is_extended_id=True,
                )
                bus.send(msg)

            print(f"\r[vcan0] Ráfaga de {len(lista_tramas)} tramas enviada", end="")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nEmulación detenida correctamente.")

if __name__ == "__main__":
    main()
