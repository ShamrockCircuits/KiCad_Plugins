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
        '''
            @param - variant_name: name to be assigned to variant (ex: 'BASE")\n
            @param - Schematic_List: List of all schematics in the project
        '''

        self.name =  variant_name.replace("Variant_", "")   # Remove the Variant tag if it was already there
        self.property_name = "Variant_" + variant_name      
        self.DNP = self.default_value                       # Overwritten when we call __AddSymbolProperties()
        self.Sch_List = Schematic_List

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
            Removes this variant from the schematic.\n
            NOTE - Must call SAVE() for changes to stick.
        '''

        for Schematic in self.Sch_List:
            for part in Schematic.symbol:
                
                if self.property_name in part.property:
                    var = part.property[self.property_name].delete()
                    pass

        return

    def LoadDNPtoVariant(self):
        '''
        This method copies the current population (DNP) displayed on the schematic and updates THIS variant with that population.\n
        Example - If your currently displaying the BASE variant, then call this method on the LITE variant, the BASE and LITE variant will \n
        now have the identical populations.\n

        Assumes Variant-xxx property already exists (must have already called AddSymbolProperties) \n
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
        return None

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
            @ param - Schematics. List of paths to schematics in the project.\n
                    - If no paths are provided this constructor tries to find schematics based on working DIR\n
            TODO - I should probably just ask for the project directory and pull all <kicad_sch> files from there\n
                 - instead of prompting the user for all the paths... 
        '''
        print("========================================================\n"
              "==================== KiCad Variants ====================\n"
              "========================================================\n"
              "  Backup your project before starting!!!  \n"
              "========================= DEMO =========================\n"
              " > paths = [<path-to-sch.kicad_sch>, <path-to-sch.kicad_sch>]\n"
              " > my_Variants = KiCadVariants.Variants(paths)\n"
              " > my_Variants.ListAllVariants()\n"
              " > my_Variants.Add_Variant('TEST')\n"
              " > my_Variants.Remove_Variant('BASE')\n"
              " > my_Variants.SAVE()\n"
              "=======================================================\n")

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
        '''
            Saves data to all schematics. \n
            Warning, this overwrites existing data. Best to keep a backup just to be safe.
        '''

        for sch in self.Sch_List:
            sch.write(sch.filepath)
            pass

    def Reload_Schematic(self):
        '''
            TLDR - Reloads sexpressions

            If you made changes to the schematic and want them to be reflected in your code, you will need to reload the schematic.
            For example, In Kicad eeschema you set the DNP's you'd like to load into the BASE variant, and save you changes.
            We must reload the sexpressions in order to "See" this change, before we can call "LoadDNPtoVariant".

            BEWARE - Any changes you made will be lost unless you call "Variant.SAVE"
        '''

        # print("BEWARE - Any changes you made will be lost unless you call 'Variant.SAVE()'...\n" 
        #       "Variant.SAVE() will also overwrite any changes on the schematic..\n"
        #       "Recommend steps --- Call Variant.SAVE() -> Make DNP changes -> Call Reload_Schematic -> continue as normal")

        # I believe this will clear everything for us
        self.__init__(self.Paths) 
         
    def Add_Variant(self, variant_name : str):
        '''
            Adds variant to this project. If Variant already exists, nothing is done. \n
            @ param - variant_name. Name that will be assigned to the variant object. EX: "BASE" will become "Variant_BASE"
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
            Remove variant_name from existing variants.\n
            Note - Call SAVE() to have these changes reflected on the schematic. \n
        '''
        var = self.__Get_Variant(variant_name)
        if type(var) != None:
            var.Remove_Variant()
            self.Variant_List.remove(var)
        return

    def LoadDNPtoVariant(self, variant_name : str):
        '''
            Loads what's 'currently' displayed on the schematic into the varient you specify.\n
            NOTE - You may need to call __Reload_Schematic() if you recently changed the schematic.\n
        '''

        self.__Get_Variant(variant_name).LoadDNPtoVariant()
        return

    def Display_Variant(self, variant_name:str):
        '''
        Updates the variant that's currently displayed on the schematics DNP.\n
        Script parses every symbol and checks its "Variant-xxx" property. \n
        If the name matches, then it updates the DNP attribute which is then displayed on the schematic. \n
        NOTE - The user must call SAVE() then close and reopen the schematic editor to see the changes.
        '''
        self.__Get_Variant(variant_name).DisplayThisVariant()

        return

    def ListAllVariants(self):
        '''
            Prints all the available variants.\n
        '''

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
            Returns variant from Variant_List of the specified name \n
            Returns None if variant doesn't exists \n
            @param - variant_name. Name of desired variant.
        '''

        for var in self.Variant_List:
            if var.name == variant_name:
                # print("__Get_Varaint() --> Found Variant")
                return var
        
        # print("__Get_Varaint() --> Not Found")
        return None

    def __Load_Existing_Variants(self) -> bool:
        '''
        Parses every schematic in the project and looks for unique Variants. \n
        Loads Variants to module, as if user called "Add_Variant()" for each one \n
        If symbols are missing variants, they will be added. \n

        return - IssueFoundFlag - Generic flag notifying the user if any new variants had to be assigned\n
        You can safely ignore the status of IssueFoundFlag. \n

        TODO - Cleanup this method, its kinda greasy
        '''

        keyword = "Variant_"            # We will look for this keyword in the symbol properties
        VaraintsFound = set()           # Reminder - Sets Only allows unique elements

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
                # This is just to notify the user, nothing is really done with the information
                if NumVariantsBefore != len(VaraintsFound):
                    print("__Load_Existing_Variants() - Found discrepancy in number of varaints... Seems like a new variant was added by " + str(part.name))
                    IssueFoundFlag = True
                
                if NumVariantsFound != NumVariantsBefore:
                    print("__Load_Existing_Variants() - Found discrepancy in number of varaints... Seems like this part was missing a variant " + str(part.name))   
                    IssueFoundFlag = True

        # Add Variants to our structure
        for var in VaraintsFound:
            self.Add_Variant(var)

        return IssueFoundFlag

    def __AutoPopulateSchPaths(self, search_path : str):
        '''
            Finds all schematics in "Search_path" with ext (.kicad_sch) \n
            Beware this method is somewhat recursive and will recall itself if some issue occurs\n
            The schematics will be stored in self.Sch_List \n
            
            @param - search_path: Existing DIR to search\n
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
            Ideally this method would actually close and reopen the schematic for the user...\n
            But for now it will just prompt the user to do it. \n
        '''
        input(">> Close and reopen schematic... *enter* to continue")
        return
