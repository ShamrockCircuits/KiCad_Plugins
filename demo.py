from KiCadVariants import KiCadVariants

# Initialize variant
my_Variants = KiCadVariants.Variants(['<path to project>'], AutoSavePrompt = False)

# Prints list of all variants
my_Variants.ListAllVariants()

# Adds the "Variant_TEST" to your project
my_Variants.Add_Variant("TEST")
my_Variants.ListAllVariants()

# Assigns currently displayed DNPs to "Variant_TEST"
my_Variants.LoadDNPtoVariant("TEST")

# We can display a different variant using
my_Variants.Display_Variant("Base")

# And we can remove the variant
my_Variants.Remove_Variant("TEST")