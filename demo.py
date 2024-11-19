from KiCadVariants import KiCadVariants
import skip

path = "C:\\Users\\jesse\\OneDrive\\Desktop\\GitHub\\Mini_Projects\\Usb_EthHUB\\PCBA\\REV1\\UsbEthHub_rev1.0\\eth-hub.kicad_sch"
sch = skip.Schematic(path)

my_Variants = KiCadVariants.Variants([sch])
my_Variants.Add_Variant("LITE")
my_Variants.Add_Variant("FULL")

print("here")