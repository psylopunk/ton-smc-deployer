from tonsdk.boc import Cell

cell = Cell()
cell.bits.write_uint(0, 32)
content = Cell()
for i in range(1, 4):
    _cell = Cell()
    _cell.bits.write_uint(i * 5, 32)
    content.refs.append(_cell)

cell.refs.append(content)

print(f"Data: {cell.to_boc(False).hex()}")

