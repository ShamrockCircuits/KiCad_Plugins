from KiCadVariants import KiCadVariants

paths = ["D:\\WS_projects\\Mini_Projects\\DemoVariantsProject\\DemoVariantsProject.kicad_sch"]


my_Variants = KiCadVariants.Variants(paths)
my_Variants.SAVE()

print("here")