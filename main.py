from models.spn import SPN
from models.pgn import PGN

# 1. Instanciar PGN 61444 (EEC1 - Datos de Motor)
eec1 = PGN(pgn_number=61444, name="Electronic Engine Controller 1", priority=3, source_address=0x00)

# 2. Instanciar SPN 190 (RPM del Motor): Res = 0.125, Offset = 0, 2 Bytes, Inicia en Byte 4
spn_rpm = SPN(
    spn_id=190,
    name="Engine Speed",
    resolution=0.125,
    offset=0.0,
    length_bytes=2,
    start_byte=4,
    min_val=0.0,
    max_val=8000.0
)

# Configurar 2100 RPM
spn_rpm.set_value(2100.0)
eec1.add_spn(spn_rpm)

# 3. Generar la trama
msg = eec1.build_message()

print(f"=== PRUEBA DE ARQUITECTURA POO ===")
print(f"PGN: {eec1.name} ({eec1.pgn_number})")
print(f"CAN ID (Hex 29-bits): {hex(msg.arbitration_id)}")
print(f"Payload Bytes (Hex) : {[hex(b) for b in msg.data]}")
