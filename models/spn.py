import struct

class SPN:
    """
    Representa un Suspect Parameter Number (SPN) dentro del estándar SAE J1939.
    Maneja la conversión entre valores en unidades de ingeniería (decimal) y bytes de payload.
    """
    def __init__(self, spn_id: int, name: str, resolution: float, offset: float, length_bytes: int, start_byte: int, min_val: float, max_val: float):
        self.spn_id = spn_id
        self.name = name
        self.resolution = resolution
        self.offset = offset
        self.length_bytes = length_bytes
        self.start_byte = start_byte  # Índice base 1 (Estándar J1939)
        self.min_val = min_val
        self.max_val = max_val
        
        # Valor actual inicializado en el mínimo permitido
        self._current_value = min_val

    def set_value(self, value: float):
        """Setea el valor clamping en el rango seguro del parámetro."""
        self._current_value = max(self.min_val, min(self.max_val, value))

    def get_value(self) -> float:
        return self._current_value

    def to_bytes(self) -> bytes:
        """
        Convierte el valor decimal actual al formato en bytes J1939 (Little-Endian).
        Fórmula: Raw = (Valor - Offset) / Resolución
        """
        raw_val = int((self._current_value - self.offset) / self.resolution)
        
        # Selección del formato struct según el tamaño del dato
        if self.length_bytes == 1:
            return struct.pack('<B', raw_val & 0xFF)
        elif self.length_bytes == 2:
            return struct.pack('<H', raw_val & 0xFFFF)
        elif self.length_bytes == 4:
            return struct.pack('<I', raw_val & 0xFFFFFFFF)
        else:
            raise ValueError(f"Longitud de bytes {self.length_bytes} no soportada actualmente.")
