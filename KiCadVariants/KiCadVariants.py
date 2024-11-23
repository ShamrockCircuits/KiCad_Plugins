# hacky hack to use local version of kicad-skip
import sys
sys.path.append('D:\\WS_projects\\GITHUB\\kicad-skip\\src')

import skip
from enum import Enum
from typing import List
import os


class ChildVariant():
    '''
        Variant Class
        Contains the information for a single variant.
    '''
    CurrentDisplayed = "_CURRENT_"  # Load the currently displayed schematic DNP
    DoNotPopulate = "DNP"
    Populate = "STUFF"
    default_value = CurrentDisplayed

    def __init__(self, variant_name : str,  Schematic_List : List['skip.Schematic']):
        self.name =  variant_name.replace("Variant_", "")   # remove the Variant tag if it was already there
        self.property_name = "Variant_" + variant_name
        self.DNP = False

        self.Sch_List = Schematic_List  # this is bad practice... probably

        # Check that this variant is already listed on the schematic part properties
        self.__AddSymbolProperties()
        pass

    def __AddSymbolProperties(self):
        '''
            Add this variant to the symbol property of EVERY part in the specified shematic.
            If variant property already exists nothing will be done for that part.

            @param - Schematic. schematic object.
        '''

        for Schematic in self.Sch_List:
            for part in Schematic.symbol:
                
                # Create the new property if it doesn'y exist yet
                if self.property_name not in part.property:
                    var = part.property.Datasheet.clone() 
                    var.name = self.property_name
                    var.value = self.default_value

                    if( self.default_value == self.CurrentDisplayed):
                        var.value = self.DoNotPopulate if part.dnp else self.Populate 
                else:
                    #Variant property already exists... though the name could be incorrect.
                    pass
        return

    def Remove_Variant(self):
        '''
            Removes this variant from the schematic. 
        '''

        for Schematic in self.Sch_List:
            for part in Schematic.symbol:
                
                if self.property_name in part.property:
                    var = part.property[self.property_name].delete()
                    pass

        return

    def LoadDNPtoVariant(self):
        '''
        This method copies the current population (DNP) displayed on the schematic and updates THIS variant with that population.

        Example - If your currently displaying the BASE variant, then call this method on the LITE variant, the BASE and LITE variant will 
        now have the identical populations.

        Assumes Variant-xxx property already exists (must have already called AddSymbolProperties)
        '''

        Variant_property = None

        for Schematic in self.Sch_List:
            for part in Schematic.symbol:

                # First find the Variant_xxx property
                if self.property_name not in part.property:
                    raise Exception("Properties does not contain variant info for " + self.property_name + 
                                    "\nEnsure " + self.property_name + " exists, before calling this class method" +
                                    "\nThis error generally means you didn't call AddSymbolProperties first")

                
                Variant_property = part.property[self.property_name]
                if part.dnp:
                    Variant_property.value = self.DoNotPopulate
                else:
                    Variant_property.value = self.Populate

    def DisplayThisVariant(self):
        '''
            Displays THIS variant on the schematic... sets DNP attributes based on Variant_xxx properties.

            @ param - list of schematics
        '''
        Variant_property = None

        for Schematic in self.Sch_List:
            for part in Schematic.symbol:

                # First find the Variant_xxx property
                if self.property_name not in part.property:
                    raise Exception("Properties does not contain variant info for " + self.property_name + 
                                    "\nEnsure " + self.property_name + " exists, before calling this class method" +
                                    "\nThis error generally means you didn't call AddSymbolProperties first")

                
                Variant_property = part.property[self.property_name]
                if Variant_property == self.Populate:
                    part.dnp = False
                else:
                    part.dnp = True
        print(">> Display variant -> " + self.property_name)
        return

class Variants():
    '''
        Class that holds and accesses all the ChildVariant() objects in a schematic.
    '''

    # TODO - Add autosave feature w/ suggestions on when to reload kicad
    def __init__(self, Project_Schematics : list[str] = None):
        '''
            @ param - Schematics. List of paths to schematics in the project.
                    - If no paths are provided this constructor tries to find schematics based on working DIR
        '''
        self.Paths = Project_Schematics
        self.Sch_List : List['skip.Schematic'] = []
        self.Variant_List : list['ChildVariant'] = []

        if Project_Schematics == None:
            if( input("No path provided using -> " + os.getcwd() +" (y/n)") == "y"):
                self.__AutoPopulateSchPaths( os.getcwd() )
            else:
                raise Exception("Error - Must provide paths")

        else:
            for path in Project_Schematics:
                self.Sch_List.append(skip.Schematic(path))

        # Add Base Variant - apply actively displayed DNP
        self.__Load_Existing_Variants()

        return

    def SAVE(self):
        for sch in self.Sch_List:
            sch.write(sch.filepath)
            pass

    def Reload_Schematic(self):
        '''
            If you made changes to the schematic and want them to be reflected in your code, you will need to reload the schematic.
            For example, In Kicad eeschema you set the DNP's you'd like to load into the BASE variant, and save you changes.
            We must reload the sexpressions in order to "See" this change, before we can call "LoadDNPtoVariant".

            TLDR - Reloads sexpressions

            BEWARE - Any changes you made will be lost unless you call "Variant.SAVE"
        '''

        print("BEWARE - Any changes you made will be lost unless you call 'Variant.SAVE()'...\n" 
              "Variant.SAVE() will also overwrite any changes on the schematic..\n"
              "Recommend steps --- Call Variant.SAVE() -> Make DNP changes -> Call Reload_Schematic -> continue as normal")

        # I believe this will clear everything for us
        self.__init__(self.Paths) 
         
    def Add_Variant(self, variant_name : str):
        '''
            Adds variant to this project.
            @ param - variant_name. Name that will be assigned to the variant object
        '''

        if( variant_name.__contains__("Variant")):
            raise Exception("Variant name must not contain the word variant... variant name should be something simple like 'BASE'")

        # Check if Variant already exists
        if self.__Get_Variant(variant_name) != None:
            print("Warning - The variant already exists... ignoring Add_Variant Request")
            return None

        variant = ChildVariant(variant_name, self.Sch_List)
        self.Variant_List.append(variant)
        return

    def Remove_Variant(self, variant_name : str):
        '''
            Tries to remove variant_name from existing variants.
            Does not check if variant exists
        '''
        var = self.__Get_Variant(variant_name)
        if type(var) != None:
            var.Remove_Variant()
            self.Variant_List.remove(var)
        return

    def LoadDNPtoVariant(self, variant_name : str):
        self.__Get_Variant(variant_name).LoadDNPtoVariant()
        return

    def Display_Variant(self, variant_name:str):
        '''
        Updates the variant that's currently displayed on the schematic
        Script parses every symbol and checks its "Variant-xxx" property.
        If the name matches, then it updates the DNP attribute which is then displayed on the schematic
        '''
        self.__Get_Variant(variant_name).DisplayThisVariant()

        return

    def ListAllVariants(self):

        txt = "Available Variants -> ["

        if len(self.Variant_List) != 0:
            for var in self.Variant_List:
                txt += var.name + ", "
        else:
            txt+= "NONExx"  #dumb I know ;)
        
        # remove that last garbage ", "
        txt = txt[:len(txt)-2] + "]"
        print(txt)
        return None

    def __Get_Variant(self, variant_name:str) -> ChildVariant:
        '''
            Returns variant from Variant_List of the specified name
            @param - variant_name. Name of desired variant
        '''

        for var in self.Variant_List:
            if var.name == variant_name:
                print("__Get_Varaint() --> Found Variant")
                return var
        
        print("__Get_Varaint() --> Not Found")
        return None

    def __Load_Existing_Variants(self):
        '''
        NOTE - I don't like this method, nor how I implemented it.
        Check what variants exist on the schematic by parsing all part properties
        If symbols are missing variants, this property will be added.
        '''

        keyword = "Variant_"            # We will look for this keyword in the symbol properties
        VaraintsFound = set()             # Reminder - Sets Only allows unique elements

        IssueFoundFlag = False          # Very generic flag, just means the len(VariantsFound) wasn't the same for all the parts

        # This is a bit excessive... and probably slow
        # We are checking EVERY symbol in EVERY schematic and making a list of all the Variant_ properties
        # If any symbol doesn't comply we will go through the symbols and add the missing varaints
        
        # Use random symbol to generate VariantsFound SET
        for property in self.Sch_List[0].symbol[0].property:
            if str(property.name).__contains__(keyword):
                 VaraintsFound.add(str(property.name).replace(keyword, ""))

        # check all schematics in the project
        for Schematic in self.Sch_List:

            # check every part in each schematic
            for part in Schematic.symbol:

                NumVariantsBefore = len(VaraintsFound)
                NumVariantsFound = 0

                # check every property in each part
                for property in part.property:

                    # Find variant properties ex:"Variant_BASE"
                    if str(property.name).__contains__(keyword):
                        NumVariantsFound += 1

                        VaraintsFound.add(str(property.name).replace(keyword, ""))

                # Determine if this part was (A) missing a varaint, or (B) had a variant that didn't exist before
                if NumVariantsBefore != len(VaraintsFound):
                    print("__Load_Existing_Variants() - Found discrepancy in number of varaints... Seems like a new variant was added by " + str(part.name))
                    IssueFoundFlag = True
                
                if NumVariantsFound != NumVariantsBefore:
                    print("__Load_Existing_Variants() - Found discrepancy in number of varaints... Seems like this part was missing a variant " + str(part.name))   
                    IssueFoundFlag = True

        # Add Variants to our structure
        for var in VaraintsFound:
            self.Add_Variant(var)

        return

    def __AutoPopulateSchPaths(self, search_path : str):
        '''
            Finds all schematics in "Search_path" with ext (.kicad_sch)
            Beware this method is somewhat recursive and will recall itself is some issue occurs
            
            @ Param - search_path. Existing DIR to search

            Return - Updates self.Sch_List with new files
        '''
        file_ext = ".kicad_sch"
        path_list = []

        # check if directory exists
        if not os.path.isdir(search_path):
           self.__AutoPopulateSchPaths( input("Invalid path please enter new path: ").strip() )

        # Find folder contains (.kicad_sch)
        for file in os.listdir():
            if file.__contains__(file_ext):
                path_list.append(file)

        # Check if any found
        if len(path_list) == 0:
           self.__AutoPopulateSchPaths( input("No ("+file_ext+") files found please enter new path: ").strip() )
        
        # push files into class variable
        self.Sch_List.clear()
        for file in path_list:
            self.Sch_List.append( skip.Schematic(file) )

        return
       
    def __ReloadProject(self):
        '''
            Saves then opens all .kicad_sch files.
            TODO - Implement this method
        '''
        print("Please close and reopen the Kicad Schematics...")
        return
