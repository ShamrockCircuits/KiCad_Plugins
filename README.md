<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/ShamrockBanner_FloatBlack.png" alt="Logo" width=600>
  </a>

  <h3 align="center">Python Enabled KiCad Variants</h3>

  <p align="center">
    An extension of Kicad-Skip that enables the management of BOM variants in your KiCad project.<br /> Posting just for reference. Users should instead see the <a href="https://github.com/markh-de/KiVar"><strong>KiVar</strong></a> package.
    <br />
    <br />
    <br />
    <a href="https://youtu.be/Ha4PHfQfXqc">View Demo</a>

  </p>
</div>







<!-- ABOUT THE PROJECT -->
## About The Project

I’ve been using KiCad for several years, and one feature I’ve been holding out hope for is project variants. A project variant is some variation of your design, typically just a population change, that enables or disables some features on in your design. The “Lite” and “Full” variants are the most common types of variants, where the “Full” variant will contain all the product features and the “Lite” will have some subset of those features, usually to reduce the cost of the device. The possibilities are endless though!

After recently watching a <a href="https://www.youtube.com/watch?v=EP1GtsZ2VfM">video</a> from <a href="https://www.youtube.com/@PsychogenicTechnologies">Psychogenic Technologies</a> I learned he recently made a Python package that lets you easily interact with KiCad Schematics. My mind immediately jumped to variants. The same weekend, I launched VS Code and started scripting. I later learned I should have searched the web more first… There is already support for variants in KiCad and it was added seemingly this year (*2024*) via the <a href="https://www.youtube.com/@PsychogenicTechnologies">KiVar plugin</a>. It looks like KiVar is very well maintained and fleshed out, so if you’re looking for variants in your KiCad project I’d highly recommend you go there.



I’ll post my project just for others to see how handy KiCad-Skip can be! But as I mentioned **please see KiVar if you’re looking to add variants to your project**.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Some steps to get this script running on your machine. Note you'll need to modify KiCad-Skip slightly, otherwise you won't be able to remove the variants that you create. See this <a href="https://github.com/psychogenic/kicad-skip/pull/12">pull request</a> on the KiCad-Skip project for details.

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Clone this repo
   ```sh
   git clone https://github.com/ShamrockCircuits/KiCad_Plugins
   ```
2. Clone KiCad-Skip
   ```sh
   git clone https://github.com/ShamrockCircuits/KiCad_Plugins
   ```
3. Add method to property.py in KiCad-Skip (see <a href="https://github.com/psychogenic/kicad-skip/pull/12">pull request</a>)
   ```py
   def delete(self):
        self.wrapped_parsed_value.delete()
        return None
   ```
5. Modify KiCadVariants.py line 3
   ```py
    sys.path.append('<path>\\kicad-skip\\src')
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
Watch video demo -> <a href="https://youtu.be/Ha4PHfQfXqc">Youtube/Kicad Variants</a>
* Calling Add_Varaint() too fast may result in the variant not saving properly. Call Reload_Schematic() to check whether the change actually stuck to the schematic.
* Please backup your project before using this code just to be safe ;)


```py
from KiCadVariants import KiCadVariants

# Initialize variant
my_Variants = KiCadVariants.Variants(['<path to project>'], AutoSavePrompt = False)

# Prints list of existing variants
my_Variants.ListAllVariants()

# Adds the "Variant_TEST" to your project
my_Variants.Add_Variant("TEST")

# We can sanity check that the change was loaded to the schematic
# By reloading the S-expressions
my_Variants.Reload_Schematic()
my_Variants.ListAllVariants()

# Assigns currently displayed DNPs to "Variant_TEST"
my_Variants.LoadDNPtoVariant("TEST")

# If "Variant_Base" already exists, we can display it using
my_Variants.Display_Variant("Base")

# And we can remove the variant
my_Variants.Remove_Variant("TEST")
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>