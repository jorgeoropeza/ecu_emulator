import can
from typing import List
from .spn import SPN

class PGN:
    """
    Representa un Parameter Group Number (PGN) de J1939.
    Ensambla múltiples SPNs dentro de un payload de 8 bytes y genera la trama de 29 bits.
    """
    def __init__(self, pgn_number: int, name: str, priority: int = 3, source_address: int = 0x00):
        self.pgn_number = pgn_number
        self.name = name
        self.priority = priority
        self.source_address = source_address
        self.spns: List[SPN] = []

    def add_spn(self, spn: SPN):
        """Añade un parámetro SPN al contenedor del PGN."""
        self.spns.append(spn)

    def calculate_can_id(self) -> int:
        """
        Calcula el Identificador CAN Extendido de 29 bits.
        Con la estructura: [3 bits Prioridad] + [18 bits PGN] + [8 bits Source Address]
        """
        can_id = (self.priority & 0x07) << 26
        can_id |= (self.pgn_number & 0x3FFFF) << 8
        can_id |= (self.source_address & 0xFF)
        return can_id

    def build_message(self) -> can.Message:
        """
        Construye el arreglo de 8 bytes (rellenando vacíos con 0xFF)
        y devuelve un objeto can.Message listo para SocketCAN.
        """
        # Inicializar los 8 bytes del payload en '0xFF' (Dato No Disponible / Relleno Estándar)
        payload = bytearray([0xFF] * 8)

        for spn in self.spns:
            spn_bytes = spn.to_bytes()
            start_index = spn.start_byte - 1  # Convertir a índice base 0 de Python
            
            # Copiar los bytes convertidos en las posiciones correspondientes
            for i, byte in enumerate(spn_bytes):
                if start_index + i < 8:
                    payload[start_index + i] = byte

        return can.Message(
            arbitration_id=self.calculate_can_id(),
            data=payload,
            is_extended_id=True
        )
