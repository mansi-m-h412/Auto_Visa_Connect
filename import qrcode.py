import qrcode
data="https://www.google.com/maps/place/Jindal+Vidya+Mandir/@15.1737957,76.5551859,13z/data=!4m10!1m2!2m1!1sjindal+vidya+mandir!3m6!1s0x3bb7655c9ed961ff:0xff57fede8be89bf6!8m2!3d15.1737957!4d76.6314036!15sChNqaW5kYWwgdmlkeWEgbWFuZGlykgELY2JzZV9zY2hvb2yqAVUQASoXIhNqaW5kYWwgdmlkeWEgbWFuZGlyKAAyHxABIhu3wKayXLI5CG4BnKr8NZDJxkOx3Pzrb2IY-ngyFxACIhNqaW5kYWwgdmlkeWEgbWFuZGly4AEA!16s%2Fg%2F1hhj5wdcm?entry=ttu&g_ep=EgoyMDI1MDcyNy4wIKXMDSoASAFQAw%3D%3D"
qr=qrcode.make(data)
qr.save("jvmschool.png")
print("qr code generated..")