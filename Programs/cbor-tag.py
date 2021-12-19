import cbor2 as cbor
from datetime import date, timezone

print (date.today())
c1 = cbor.dumps(date.today(), timezone=timezone.utc, date_as_datetime=True)

print (c1.hex())

print (cbor.loads(c1))
print (type(cbor.loads(c1)))



