import datetime
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable

# This object holds valid tag with their level
# Tag with other key value pair then this will considered as Invalid
allowedTags = {
    'HEAD': '0', 'NOTE': '0', 'NAME': '1', 'INDI': '0', 'SEX': '1', 'BIRT': '1', 'DATE': '2', 'FAM': '0',
    'FAMS': '1', 'FAMC': '1', 'DEAT': '1', 'HUSB': '1', 'WIFE': '1', 'CHIL': '1', 'MARR': '1', 'DIV': '1',
    'TRLR': '0'
}

# Replace your file name here check data for individuals and families
fileName = "input.ged"

# This function reads file and stor`e all lines in one variable
with open(fileName, 'r') as file:
    lines = file.read().splitlines()
lines = [[line] for line in lines]

sprint1CodeOutput = open("input.ged.ged", "a")
sprint1CodeOutput.truncate(0)

# this for loop is finding any gedcom line with errors
# if line is not having tag or level it will set error to lines
for i in range(len(lines)):
    if ((len(lines[i][0].split())) < 2):
        lines[i] = "error at line number " + str(i)
    else:
        lines[i] = lines[i][0].split(" ", 2)
        if (len(lines[i]) > 2 and lines[i][2] in ["INDI", "FAM"]):
            lines[i][1], lines[i][2] = lines[i][2], lines[i][1]
        elif (len(lines[i]) > 2 and lines[i][1] in ["INDI", "FAM"]):
            lines[i] = "Error at line number " + i

# This array holds all gedcom entries which has valid tag and level
# It will be used for further data processing of individuals and families.
infoList = []
for i in range(len(lines)):
    if (len(lines[i]) > 2):
        # line has valid tag and level it will add to infolist
        if (lines[i][1] in allowedTags.keys() and allowedTags[lines[i][1]] == lines[i][0]):
            infoList.append((lines[i][0], lines[i][1], lines[i][2]))
        elif (lines[i][0:2] == "In"):
            infoList.append(lines[i])
    # If line has valid tag and level it means it has data of person or family
    elif (len(lines[i]) == 2):
        if ((lines[i][1] in allowedTags.keys()) and allowedTags[lines[i][1]] == lines[i][0]):
            infoList.append((lines[i][0], lines[i][1]))

# Removing unwanted data
# this line is used to remove HEAD tag
infoList.pop(0)
# This line is used to remove TRLR tag
infoList.pop(-1)
# This line is used to remove lines which has level 1 and tag birt
infoList = list(filter((('1', 'BIRT')).__ne__, infoList))

# Flag variable to determing when to stop crawling for individuals
shouldBreak = False
# This both object holds data with tag for individuals and family where key will be id of individual and family
individualsData = {}
familiesData = {}
# Iterating infolist to get infomation of individuals
for i in range(len(infoList)):
    # This array holds array of tag and its value
    vals = []
    j = i + 1
    if (infoList[i][1] == 'INDI' and infoList[i][0] == '0'):
        # this loop will get all infomation about individual
        while (infoList[j][1] != 'INDI'):
            # Key holds the ID of specific individuals
            key = infoList[i][2][1:-1]
            # If we found beggining of family records we will stop execution for individual data gathering
            if (infoList[j][1] == 'FAM' and infoList[j][0] == '0'):
                shouldBreak = True
                break
            elif (infoList[j][1] == 'DEAT' and infoList[j][2] == 'Y'):
                vals.append(('DEAT', infoList[j + 1][2]))
                j += 1
            elif (infoList[j][1] == 'FAMC' or infoList[j][1] == 'FAMS'):
                vals.append((infoList[j][1], infoList[j][2][1:-1]))
            else:
                vals.append((infoList[j][1], infoList[j][2]))
            j += 1
        individualsData.update({key: vals})
        if (shouldBreak):
            break

# Columns of individuals table
individualsTable = PrettyTable(["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"])
# This array holds array of individual information
individuals = []

# Iteraing over individuals data and getting only values needed for output
for key, value in individualsData.items():
    age = 0
    name = ""
    gender = ""
    birthday = ""
    death = "NA"
    isAlive = False
    for i in range(len(value)):
        famc = []
        fams = []
        if (value[i][0] == "NAME"):
            temp = value[i][1]
            if (len(temp) == 0):
                temp = "NA"
            name = temp

        if (value[i][0] == "SEX"):
            temp = value[i][1]
            if (len(temp) == 0):
                temp = "NA"
            gender = temp

        if (value[i][0] == "DATE"):
            temp = datetime.datetime.strptime(value[i][1], "%d %b %Y").date()
            if (len(str(temp)) == 0):
                temp = "NA"
            birthday = temp

        if (value[i][0] == "DEAT"):
            temp = datetime.datetime.strptime(value[i][1], "%d %b %Y").date()
            if (len(str(temp)) == 0):
                temp = "NA"
            death = temp

        if (value[i][0] == "FAMC"):
            temp = value[i][1]
            if (len(temp) == 0):
                temp = "NA"
            famc.append(temp)

        if (value[i][0] == "FAMS"):
            temp = value[i][1]
            if (len(temp) == 0):
                temp = "NA"
            fams.append(temp)
    # Finding is individual alive or not.
    if (any("DEAT" in i for i in value)):
        age = relativedelta(death, birthday).years
    else:
        age = relativedelta(datetime.datetime.now(), birthday).years
        isAlive = True

    # Formating array representation
    if (len(famc) == 0):
        famc = "NA"
    else:
        famc = str(famc)
        famc = famc.replace("[", "{").replace("]", "}")

    if (len(fams) == 0):
        fams = "NA"
    else:
        fams = str(fams)
        fams = fams.replace("[", "{").replace("]", "}")

    individuals.append([key, name, gender, str(birthday), age, isAlive, str(death), famc, fams])

individualsTable.add_rows(individuals)

# Showing individuals details
# print("Individuals")
# print(individualsTable)
print("Individuals", file=sprint1CodeOutput)
print(individualsTable, file=sprint1CodeOutput)

# Iterating over infolist of gather information for families
for i in range(len(infoList)):
    # This array variable holds array of tag regarding family and its value
    vals = []
    j = i + 1
    if (infoList[i][1] == 'FAM' and infoList[i][0] == '0'):
        while (j < len(infoList)):
            key = infoList[i][2][1:-1]
            # This if block find individuals id for spouce and childern
            if (infoList[j][1] != "MARR" and infoList[j][1] != "DIV" and infoList[j][1] != "DATE" and infoList[j][
                1] != "FAM"):
                vals.append((infoList[j][1], infoList[j][2][1:-1]))
            # This else if block find divorce date if there is any happen
            elif (infoList[j][1] == "DIV" and len(infoList[j + 1]) > 2):
                vals.append(("DIV", infoList[j + 1][2]))
            # This else if block finds marriage date
            elif (infoList[j][1] == "MARR" and len(infoList[j + 1]) > 2):
                vals.append(("MARR", infoList[j + 1][2]))
            # If new family is started then this loop is stopped
            elif (infoList[j][1] == "FAM" and infoList[j][0] == "0"):
                break
            j += 1
        familiesData.update({key: vals})

# Columns names for family table
famliesTable = PrettyTable(
    ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
# This array holds array of family details
families = []
for key, value in familiesData.items():
    innerChild = []
    married = ""
    divorce = ""
    husbandId = 0
    wifeId = 0
    husbandName = ""
    wifeName = ""
    for i in range(len(value)):
        # This finds husband name
        if (value[i][0] == "HUSB"):
            husbandId = value[i][1]
            husbandName = individualsData[husbandId][0][1]
        # This finds wife name
        if (value[i][0] == "WIFE"):
            wifeId = value[i][1]
            wifeName = individualsData[wifeId][0][1]
        # This collect children name in array
        if (value[i][0] == "CHIL"):
            child = value[i][1]
            innerChild.append(child)
        # This finds marriage date
        if (value[i][0] == "MARR"):
            married = datetime.datetime.strptime(value[i][1], "%d %b %Y").date()
        # This finds divorce date
        if (value[i][0] == "DIV"):
            divorce = datetime.datetime.strptime(value[i][1], "%d %b %Y").date()
    tempArr = [key, married, divorce, husbandId, husbandName, wifeId, wifeName]
    # Putting NA to data if there is no data.
    for i in range(len(tempArr)):
        if (len(str(tempArr[i])) == 0):
            tempArr[i] = "NA"
    # Formatting array reprentation
    if (len(innerChild) == 0):
        innerChild = "NA"
    else:
        innerChild = str(innerChild)
        innerChild = innerChild.replace("[", "{").replace("]", "}")
    tempArr.append(innerChild)
    families.append(tempArr)

# Adding family details to family table
famliesTable.add_rows(families)

# Showing family table
# print("Families")
# print(famliesTable)
print("Families", file=sprint1CodeOutput)
print(famliesTable, file=sprint1CodeOutput)

# Declaring constant for indexes of individuals and family
IDX_IND_ID = 0
IDX_IND_NAME = 1
IDX_IND_GENDER = 2
IDX_IND_BIRTHDAY = 3
IDX_IND_AGE = 4
IDX_IND_ALIVE = 5
IDX_IND_DEATH = 6
IDX_IND_CHILD = 7
IDX_IND_SPOUCE = 8

IDX_FAM_ID = 0
IDX_FAM_MARRIED = 1
IDX_FAM_DIVORCED = 2
IDX_FAM_HUSBAND_ID = 3
IDX_FAM_HUSBAND_NAME = 4
IDX_FAM_WIFE_ID = 5
IDX_FAM_WIFE_NAME = 6
IDX_FAM_CHILD = 7


# User story US03
# Story Name: Birth before death
# Owner: Sheshendra desiboyina (sd)
# Email: sdesiboy@stevens.edu
def us03_birth_before_death(individuals):
    data = []
    # Iterating over individuals data and finding birth and death date
    for individual in individuals:
        death = individual[IDX_IND_DEATH]
        birth = individual[IDX_IND_BIRTHDAY]
        if (death == "NA"):
            continue
        if (birth == "NA"):
            continue
        # Converting string date to date object
        birth = datetime.datetime.strptime(birth, "%Y-%m-%d").date()
        death = datetime.datetime.strptime(death, "%Y-%m-%d").date()

        # Comparing birth and death date to find death should not occure before birth
        if (birth < death):
            data.append("Error: INDIVIDUAL US03 " + str(individual[0]) + ": " + "named: " + str(
                individual[1]) + " Died: " + str(individual[6] + " before born at " + str(individual[3])))
    return data


data = us03_birth_before_death(individuals)
print(*data, sep="\n")
print(*data, sep="\n", file=sprint1CodeOutput)


# User story US06
# Story Name: Divorce before death
# Owner: Sheshendra desiboyina (sd)
# Email: sdesiboy@stevens.edu
import datetime

def us06_divorce_before_death(families, individuals):
    data = []
    for family in families:
        husbandId = family[IDX_FAM_HUSBAND_ID]
        wifeId = family[IDX_FAM_WIFE_ID]
        divorceDate_str = family[IDX_FAM_DIVORCED]

        # Check if divorce date is 'NA'
        if divorceDate_str == 'NA':
            continue

        isHusbandAlive = True
        isWifeAlive = True
        husbandDeath = None
        wifeDeath = None

        for individual in individuals:
            if individual[IDX_IND_ID] == husbandId:
                isHusbandAlive = individual[IDX_IND_ALIVE]
                if not isHusbandAlive and individual[IDX_IND_DEATH] != 'NA':
                    husbandDeath = datetime.datetime.strptime(individual[IDX_IND_DEATH], "%Y-%m-%d").date()
            if individual[IDX_IND_ID] == wifeId:
                isWifeAlive = individual[IDX_IND_ALIVE]
                if not isWifeAlive and individual[IDX_IND_DEATH] != 'NA':
                    wifeDeath = datetime.datetime.strptime(individual[IDX_IND_DEATH], "%Y-%m-%d").date()

        # Check if husband or wife is not alive and their death date is before divorce date
        divorceDate = datetime.datetime.strptime(str(divorceDate_str), "%Y-%m-%d").date()
        if not isHusbandAlive and (husbandDeath is not None and divorceDate < husbandDeath):
            data.append("ERROR: US06 Family: " + str(family[IDX_IND_ID]) + " husband died on " + str(
                husbandDeath) + " before their divorce date " + str(divorceDate))
        elif not isWifeAlive and (wifeDeath is not None and divorceDate < wifeDeath):
            data.append("ERROR: US06 Family: " + str(family[IDX_IND_ID]) + " wife died on " + str(
                wifeDeath) + " before their divorce date " + str(divorceDate))

    return data
data = us06_divorce_before_death(families, individuals)
print(*data, sep="\n")
print(*data, sep="\n", file=sprint1CodeOutput)


# User story US01
# Story Name: Dates before current date
# Owner: Jyotiraditya deora (jd)
# Email: jdeora@stevens.edu
import datetime

def us01_dates_before_current_date(individuals, families):
    errors = []
    current_date = datetime.datetime.now().date()

    for individual in individuals:
        # Check birth date
        if individual[IDX_IND_BIRTHDAY] != 'NA':
            try:
                birth_date = datetime.datetime.strptime(str(individual[IDX_IND_BIRTHDAY]), "%Y-%m-%d").date()
                if birth_date < current_date:
                    errors.append("ERROR: US01 Individual: {} has birth date {} before current date."
                                  .format(individual[IDX_IND_ID], individual[IDX_IND_BIRTHDAY]))
            except ValueError:
                errors.append("ERROR: US01 Individual: {} has invalid birth date format."
                              .format(individual[IDX_IND_ID]))

        # Check death date
        if individual[IDX_IND_DEATH] != 'NA':
            try:
                death_date = datetime.datetime.strptime(str(individual[IDX_IND_DEATH]), "%Y-%m-%d").date()
                if death_date < current_date:
                    errors.append("ERROR: US01 Individual: {} has death date {} before current date."
                                  .format(individual[IDX_IND_ID], individual[IDX_IND_DEATH]))
            except ValueError:
                errors.append("ERROR: US01 Individual: {} has invalid death date format."
                              .format(individual[IDX_IND_ID]))

    for family in families:
        # Check marriage date
        if family[IDX_FAM_MARRIED] != 'NA':
            try:
                marriage_date = datetime.datetime.strptime(str(family[IDX_FAM_MARRIED]), "%Y-%m-%d").date()
                if marriage_date < current_date:
                    errors.append("ERROR: US01 Family: {} has marriage date {} before current date."
                                  .format(family[IDX_FAM_ID], family[IDX_FAM_MARRIED]))
            except ValueError:
                errors.append("ERROR: US01 Family: {} has invalid marriage date format."
                              .format(family[IDX_FAM_ID]))

        # Check divorce date
        if family[IDX_FAM_DIVORCED] != 'NA':
            try:
                divorce_date = datetime.datetime.strptime(str(family[IDX_FAM_DIVORCED]), "%Y-%m-%d").date()
                if divorce_date < current_date:
                    errors.append("ERROR: US01 Family: {} has divorce date {} before current date."
                                  .format(family[IDX_FAM_ID], family[IDX_FAM_DIVORCED]))
            except ValueError:
                errors.append("ERROR: US01 Family: {} has invalid divorce date format."
                              .format(family[IDX_FAM_ID]))

    return errors
data = us01_dates_before_current_date(individuals, families)
print(*data, sep="\n")
print(*data, sep="\n", file=sprint1CodeOutput)



# User story US04
# Story Name: Marriage before divorce
# Owner: Jyotiraditya deora (jd)
# Email: jdeora@stevens.edu
import datetime


def us04_marriage_before_divorce(families):
    errors = []

    for family in families:
        # Check if marriage date is available
        if family[IDX_FAM_MARRIED] != 'NA':
            try:
                marriage_date = datetime.datetime.strptime(str(family[IDX_FAM_MARRIED]), "%Y-%m-%d").date()
            except ValueError:
                errors.append("ERROR: US04 Family: {} has invalid marriage date format."
                              .format(family[IDX_FAM_ID]))
                continue  # Skip to the next family if marriage date is invalid
        else:
            continue  # Skip to the next family if marriage date is not available

        # Check if divorce date is available
        if family[IDX_FAM_DIVORCED] != 'NA':
            try:
                divorce_date = datetime.datetime.strptime(str(family[IDX_FAM_DIVORCED]), "%Y-%m-%d").date()
            except ValueError:
                errors.append("ERROR: US04 Family: {} has invalid divorce date format."
                              .format(family[IDX_FAM_ID]))
                continue  # Skip to the next family if divorce date is invalid

            # Check if marriage date is after divorce date
            if marriage_date < divorce_date:
                errors.append("ERROR: US04 Family: {} has marriage date {} before divorce date {}."
                              .format(family[IDX_FAM_ID], family[IDX_FAM_MARRIED], family[IDX_FAM_DIVORCED]))
        else:
            continue  # Skip to the next family if divorce date is not available

    return errors
data = us04_marriage_before_divorce(families)
print(*data, sep="\n")
print(*data, sep="\n", file=sprint1CodeOutput)



