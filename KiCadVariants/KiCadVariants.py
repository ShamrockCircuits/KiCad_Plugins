import skip
from enum import Enum
from typing import List
import os


class ChildVariant():
    '''
        Variant Class
        Contains the information for a single variant.
    '''
    DoNotPopulate = "DNP"
    Populate = "STUFF"
    default_value = Populate


    def __init__(self, variant_name : str,  Schematic_List : List['skip.Schematic']):
        self.name =  variant_name.replace("Variant_", "")   # remove the Variant tag if it was already there
        self.property_name = "Variant_" + variant_name
        self.DNP = False

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
                
                if self.property_name not in part.property:
                    var = part.property.Datasheet.clone() 
                    var.name = self.property_name
                    var.value = self.default_value
                    # TODO - Figure out how to set the property to hidden, current workaround just clone a property that's already hidden
                else:
                    #Variant property already exists... though the name could be incorrect.
                    pass
        return

    def RemoveVariantFromSchematic(self):
        '''
            Removes this variant from the schematic. 
        '''
        print(">> RemoveVariantFromSchematic() - method currently not implemented, not sure if possible to delete property")

        for Schematic in self.Sch_List:
            for part in Schematic.symbol:
                
                if self.property_name in part.property:
                    # var = part.property[self.property_name].delete()
                    pass

        return

    def PushDisplayedDNPtoVariant(self):
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
        Contains information for all variants in a project.


    '''

    def __init__(self, Project_Schematics : list[str] = None):
        '''
            @ param - Schematics. List of paths to schematics in the project.
                    - If no paths are provided this constructor tries to find schematics based on working DIR
        '''

        self.Sch_List : List['skip.Schematic'] = []
        self.Variant_List : list['ChildVariant'] = []

        if Project_Schematics == None:
            print("No path provided using -> " + os.getcwd() )
            self.__AutoPopulateSchPaths( os.getcwd() )

        else:
            for path in Project_Schematics:
                    self.Sch_List(skip.Schematic(path))

        # Add Base Variant - apply actively displayed DNP
        self.Add_Variant("BASE")
        self.Variant_List[0].PushDisplayedDNPtoVariant(self.Sch_List)

        pass

    def Load_Existing_Variants(self):
        '''
        NOTE - I don't like this method, nor how I implemented it.
        Check what variants exist on the schematic by parsing all part properties
        If symbols are missing variants, this property will be added.
        '''

        keyword = "Variant_"            # We will look for this keyword in the symbol properties
        VaraintsFound : set[str] = []   # Reminder - Sets Only allows unique elements

        IssueFoundFlag = False          # Very generic flag, just means the len(VariantsFound) wasn't the same for all the parts

        # This is a bit excessive... and probably slow
        # We are checking EVERY symbol in EVERY schematic and making a list of all the Variant_ properties
        # If any symbol doesn't comply we will go through the symbols and add the missing varaints
        
        # Use random symbol to generate VariantsFound SET
        for property in self.Sch_List[0].symbol[0].property:
            if str(property.name).__contains__(keyword):
                 VaraintsFound.add(property.name)

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
                        VaraintsFound.add(property.name)

                # Determine if this part was (A) missing a varaint, or (B) had a variant that didn't exist before
                if NumVariantsBefore != len(VaraintsFound):
                    print("Load_Existing_Variants() - Found discrepancy in number of varaints... Seems like a new variant was added by " + str(part.name))
                    IssueFoundFlag = True
                
                if NumVariantsFound != NumVariantsBefore:
                    print("Load_Existing_Variants() - Found discrepancy in number of varaints... Seems like this part was missing a variant " + str(part.name))   
                    IssueFoundFlag = True

        # Add Variants to our structure
        for var in VaraintsFound:
            self.Add_Variant(var)

        return
        
    def Add_Variant(self, variant_name : str):
        '''
            Adds variant to this project.
            @ param - variant_name. Name that will be assigned to the variant object
        '''

        variant = ChildVariant(variant_name, self.Sch_List)
        self.Variant_List.append(variant)
        pass

    def Remove_Variant(self, variant_name : str):
        '''
            Tries to remove variant_name from existing variants.
            Does not check if variant exists
        '''
        self.__Get_Variant(variant_name).RemoveVariantFromSchematic()
        self.Variant_List.remove(variant_name)
        return


    def __Get_Variant(self, variant_name:str) -> ChildVariant:
        '''
            Returns variant from Variant_List of the specified name
            @param - variant_name. Name of desired variant
        '''

        for var in self.Variant_List:
            if var.name == variant_name:
                print("__Get_Varaint() --> Found Variant")
                return var
        
        print("__Get_Varaint() --> Found Variant")
        return None
            
    def Display_Variant(self, variant_name:str):
        '''
        Updates the variant that's currently displayed on the schematic
        Script parses every symbol and checks its "Variant-xxx" property.
        If the name matches, then it updates the DNP attribute which is then displayed on the schematic
        '''
        self.__Get_Variant(variant_name).DisplayThisVariant()

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
