from KiCadVariants import KiCadVariants

my_Variants = KiCadVariants.Variants(None, AutoSavePrompt = False)
my_Variants.ListAllVariants()

my_Variants.Add_Variant("TEST")
my_Variants.ListAllVariants()
my_Variants.Remove_Variant("TEST")

print("here")