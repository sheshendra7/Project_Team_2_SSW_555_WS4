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
fileName = "gedcom.ged"

# This function reads file and stor`e all lines in one variable
with open(fileName, 'r') as file:
    lines = file.read().splitlines()
lines = [[line] for line in lines]

sprint1CodeOutput = open("gedcom.ged", "a")
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

# User story US02
# Story Name: Birth before death
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def us02_birth_before_marriage(individuals):
    data = []
    
    for individual in individuals:
        marriage_date = individual[IDX_IND_MARRIAGE]
        birth_date = individual[IDX_IND_BIRTHDAY]
        
        if marriage_date == "NA" or birth_date == "NA":
            continue

        marriage_date = datetime.datetime.strptime(marriage_date, "%Y-%m-%d").date()
        birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()

        if marriage_date < birth_date:
            data.append(f"ERROR: US03 Individual {individual[IDX_IND_ID]}: {individual[IDX_IND_NAME]} - Marriage date {marriage_date} is before birth date {birth_date}")
    
    return data


# User story US05
# Story Name: Marriage before death
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def us05_marriage_before_death(individuals):
    data = []

    for individual in individuals:
        marriage_date = individual[IDX_IND_MARRIAGE]
        death_date = individual[IDX_IND_DEATH]

        if marriage_date == "NA" or death_date == "NA":
            continue

        marriage_date = datetime.datetime.strptime(marriage_date, "%Y-%m-%d").date()
        death_date = datetime.datetime.strptime(death_date, "%Y-%m-%d").date()

        if marriage_date > death_date:
            data.append(f"ERROR: US06 Individual {individual[IDX_IND_ID]}: {individual[IDX_IND_NAME]} - Marriage date {marriage_date} is after death date {death_date}")
    
    return data


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

# User story US07
# Story Name: less then 150 years old ( dead )
# Owner: Jyotiraditya deora (jd)
# Email: jdeora@stevens.edu

import datetime

def us07_less_than_150_years_old(individuals):
    errors = []
    current_date = datetime.datetime.now().date()

    for individual in individuals:
        if individual[IDX_IND_BIRTHDAY] != 'NA' and individual[IDX_IND_DEATH] != 'NA':
            try:
                birth_date = datetime.datetime.strptime(str(individual[IDX_IND_BIRTHDAY]), "%Y-%m-%d").date()
                death_date = datetime.datetime.strptime(str(individual[IDX_IND_DEATH]), "%Y-%m-%d").date()

                age_at_death = death_date.year - birth_date.year - ((death_date.month, death_date.day) < (birth_date.month, birth_date.day))

                if age_at_death<= 150:
                    errors.append("ERROR: US07 Individual: {} has age at death {} years, which is 150 years or more."
                                  .format(individual[IDX_IND_ID], age_at_death))

            except ValueError:
                errors.append("ERROR: US07 Individual: {} has invalid birth or death date format."
                              .format(individual[IDX_IND_ID]))

    return errors
data_us07 = us07_less_than_150_years_old(individuals)
print(*data_us07, sep="\n")
print(*data_us07, sep="\n", file=sprint1CodeOutput)

# User story US08
# Story Name: birth before marriage of parents
# Owner: Jyotiraditya deora (jd)
# Email: jdeora@stevens.edu
import datetime

# Assuming the indices for individuals and families are defined
IDX_FAM_MARRIED = 1
IDX_FAM_CHILD = 7
IDX_FAM_ID = 0
IDX_IND_ID = 0
IDX_IND_BIRTHDAY = 3

def parse_date(date_str):
    if isinstance(date_str, datetime.date):
        return date_str
    if date_str != 'NA':
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

def us08_birth_before_marriage_of_parents(individuals, families):
    errors = []

    for family in families:
        if family[IDX_FAM_MARRIED] != 'NA':
            marriage_date = parse_date(family[IDX_FAM_MARRIED])

            if marriage_date:
                children_ids = family[IDX_FAM_CHILD].replace("'", "").replace("{", "").replace("}", "").split(", ")

                for child_id in children_ids:
                    child_birth_date = None

                    for individual in individuals:
                        if individual[IDX_IND_ID] == child_id and individual[IDX_IND_BIRTHDAY] != 'NA':
                            child_birth_date = parse_date(individual[IDX_IND_BIRTHDAY])
                            break

                    if child_birth_date and child_birth_date < marriage_date:
                        errors.append("ERROR: US08 Family: {} Child: {} was born before parents' marriage date."
                                      .format(family[IDX_FAM_ID], child_id))
                    else:
                        print("DEBUG: No error found for Family: {} Child: {}".format(family[IDX_FAM_ID], child_id))
                print("DEBUG: Checked all children for Family: {}".format(family[IDX_FAM_ID]))
            else:
                print("DEBUG: Invalid marriage date for Family: {}".format(family[IDX_FAM_ID]))
        else:
            print("DEBUG: No marriage date for Family: {}".format(family[IDX_FAM_ID]))

    return errors

# Example usage
data_us08 = us08_birth_before_marriage_of_parents(individuals, families)
print(*data_us08, sep="\n")


# User story US21
# Story Name: Correct gender for role
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def us21_reject_illegitimate_genders(individuals, families):
    bad_genders = []
    valid = True

    for family in families:
        husband_id = family[IDX_FAM_HUSB]
        wife_id = family[IDX_FAM_WIFE]

        husband = next((ind for ind in individuals if ind[IDX_IND_ID] == husband_id), None)
        wife = next((ind for ind in individuals if ind[IDX_IND_ID] == wife_id), None)

        if husband and husband[IDX_IND_GENDER] != "M":
            bad_genders.append(f"Invalid gender for husband in family {family[IDX_FAM_ID]}: {husband[IDX_IND_NAME]}")
            valid = False

        if wife and wife[IDX_IND_GENDER] != "F":
            bad_genders.append(f"Invalid gender for wife in family {family[IDX_FAM_ID]}: {wife[IDX_IND_NAME]}")
            valid = False

    return ["US21", "Reject Illegitimate Genders", "", valid, "\n".join(bad_genders)]


# User story US42
# Story Name: Reject Illegitimate Dates
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def us42_reject_illegitimate_dates(individuals, families):
    bad_dates = []
    valid = True

    for individual in individuals:
        birth_date = individual[IDX_IND_BIRTH]
        marriage_date = individual[IDX_IND_MARRIAGE]
        death_date = individual[IDX_IND_DEATH]

        # Check birth date
        if birth_date != "NA":
            birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
            if birth_date.month == 2 and birth_date.day > 29:
                bad_dates.append(f"{individual[IDX_IND_NAME]} has an illegitimate birth date: {birth_date}")
                valid = False

        # Check marriage date
        if marriage_date != "NA":
            marriage_date = datetime.datetime.strptime(marriage_date, "%Y-%m-%d").date()
            if marriage_date.month == 2 and marriage_date.day > 29:
                bad_dates.append(f"{individual[IDX_IND_NAME]} has an illegitimate marriage date: {marriage_date}")
                valid = False

        # Check death date
        if death_date != "NA":
            death_date = datetime.datetime.strptime(death_date, "%Y-%m-%d").date()
            if death_date.month == 2 and death_date.day > 29:
                bad_dates.append(f"{individual[IDX_IND_NAME]} has an illegitimate death date: {death_date}")
                valid = False

    return ["US42", "Reject Illegitimate Dates", "", valid, "\n".join(bad_dates)]



# User story US20
# Story Name: Aunts and Uncles
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def us20_aunts_and_uncles(individuals, families):
    bad_relationships = []
    valid = True

    # Create a dictionary to map individuals to their spouses
    spouse_map = {}
    for family in families:
        husband_id = family[IDX_FAM_HUSB]
        wife_id = family[IDX_FAM_WIFE]
        spouse_map[husband_id] = wife_id
        spouse_map[wife_id] = husband_id

    for family in families:
        husband_id = family[IDX_FAM_HUSB]
        wife_id = family[IDX_FAM_WIFE]

        # Find the siblings of husband and wife
        husband_siblings = set()
        wife_siblings = set()

        for ind in individuals:
            if ind[IDX_IND_ID] in spouse_map:
                spouse_id = spouse_map[ind[IDX_IND_ID]]
                if spouse_id != husband_id and spouse_id != wife_id:
                    # This person is a sibling of either the husband or wife
                    if ind[IDX_IND_GENDER] == "M":
                        husband_siblings.add(ind[IDX_IND_ID])
                    else:
                        wife_siblings.add(ind[IDX_IND_ID])

        # Check if aunts/uncles are married to nieces/nephews
        for ind in individuals:
            ind_id = ind[IDX_IND_ID]
            if ind[IDX_IND_ID] in spouse_map:
                spouse_id = spouse_map[ind[IDX_IND_ID]]
                if ind[IDX_IND_GENDER] == "M" and spouse_id in wife_siblings:
                    bad_relationships.append(f"{ind[IDX_IND_NAME]} is married to his niece: {individuals[wife_siblings]}")
                    valid = False
                elif ind[IDX_IND_GENDER] == "F" and spouse_id in husband_siblings:
                    bad_relationships.append(f"{ind[IDX_IND_NAME]} is married to her nephew: {individuals[husband_siblings]}")
                    valid = False

    return ["US20", "No Aunts and Uncles Married to Nieces and Nephews", "", valid, "\n".join(bad_relationships)]


# User story US11
# Story Name: No bigamy
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def us11_no_bigamy(individuals, families):
    bigamous_relationships = []
    valid = True

    # Create a dictionary to track the current spouses of individuals
    current_spouses = {}

    for family in families:
        husband_id = family[IDX_FAM_HUSB]
        wife_id = family[IDX_FAM_WIFE]

        # Check the husband's current spouse
        if husband_id in current_spouses:
            bigamous_relationships.append(f"{individuals[husband_id][IDX_IND_NAME]} is already married to {individuals[current_spouses[husband_id]][IDX_IND_NAME]} before marrying {individuals[wife_id][IDX_IND_NAME]}")
            valid = False
        else:
            current_spouses[husband_id] = wife_id

        # Check the wife's current spouse
        if wife_id in current_spouses:
            bigamous_relationships.append(f"{individuals[wife_id][IDX_IND_NAME]} is already married to {individuals[current_spouses[wife_id]][IDX_IND_NAME]} before marrying {individuals[husband_id][IDX_IND_NAME]}")
            valid = False
        else:
            current_spouses[wife_id] = husband_id

    return ["US11", "No Bigamy", "", valid, "\n".join(bigamous_relationships)]



# User story US34
# Story Name: List large age differences
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

from datetime import datetime, timedelta

def largeAgeDifferences(inputIndi, inputFam):
    errors = []
    # Create dictionaries for quick lookup
    individuals = {indi[0]: datetime.strptime(indi[3], '%Y-%m-%d') for indi in inputIndi}
    
    for fam in inputFam:
        if fam[1] != "NA":
            try:
                husbandBirthDate = individuals.get(fam[3], datetime.min)
                wifeBirthDate = individuals.get(fam[5], datetime.min)
                marriageDate = datetime.strptime(fam[1], '%Y-%m-%d')
                
                ageDiffHusband = marriageDate - husbandBirthDate
                ageDiffWife = marriageDate - wifeBirthDate

                if ageDiffHusband >= ageDiffWife * 2:
                    errors.append(f"ERROR: INDIVIDUAL: US34: {fam[3]} is over twice as old as {fam[5]} at their time of marriage")
                if ageDiffWife >= ageDiffHusband * 2:
                    errors.append(f"ERROR: INDIVIDUAL: US34: {fam[5]} is over twice as old as {fam[3]} at their time of marriage")
                
            except ValueError as e:
                print(f"Invalid date format encountered: {e}")

    for error in errors:
        print(error)
        
    return errors




# User story US36
# Story Name: List recent deaths
# Owner: Jack Gibson (jg)
# Email: jgibson2@stevens.edu

def recentDeaths(inputIndi):
    notes = []
    todayDate = datetime.now()

    for indi in inputIndi:
        if indi[5] != "True":  # Assuming 'True' means alive
            try:
                deathDate = datetime.strptime(indi[6], '%Y-%m-%d')
                if (todayDate - deathDate).days < 30:
                    note = f"NOTE: INDIVIDUAL: US36: ID: {indi[0]}: Death has occurred within the past 30 days"
                    print(note)
                    notes.append(note)
            except ValueError as e:
                print(f"Invalid date format for death date encountered: {e}")

    return notes



# User story US16
# Story Name: Male Last Names
# Owner: Sheshendra D(sd)
# Email: sdesiboy@stevens.edu
def us16_male_last_names():
    data = []

    for family in families:
        husbandName = family[IDX_FAM_HUSBAND_NAME]
        names = husbandName.split("/")
        if (len(names) < 2):
            continue
        familyLastName = names[1].strip()
        children_ids = family[IDX_FAM_CHILD]
        children_ids = children_ids.replace("{", "").replace("}", "").replace("'", "").replace(" ", "").split(",")
        for individual in individuals:
            if (individual[IDX_IND_ID] not in children_ids):
                continue
            if (individual[IDX_IND_GENDER] != "M"):
                continue
            name = individual[IDX_IND_NAME].split("/")
            if (len(name) < 2):
                continue
            lastName = name[1]
            if (lastName != familyLastName):
                data.append("ERROR US16 Family: " + str(family[IDX_IND_ID]) + " is having child named: " + individual[
                    IDX_IND_NAME] + " is having different last name")
    return data


data = us16_male_last_names()
print(*data, sep="\n")
print(*data, sep="\n", file=sprint1CodeOutput)

# User story US31
# Story Name: List living single
# Owner: Sheshendra D(sd)
# Email: sdesiboy@stevens.edu
def us31_list_living_single():
    data = []
    idOfPeopleWhoAreMarriedAtleastOne = []
    for family in families:
        idOfPeopleWhoAreMarriedAtleastOne.append(family[IDX_FAM_HUSBAND_ID])
        idOfPeopleWhoAreMarriedAtleastOne.append(family[IDX_FAM_WIFE_ID])
    for individual in individuals:
        age = individual[IDX_IND_AGE]
        if (age < 30):
            continue
        if (individual[IDX_IND_ID] in idOfPeopleWhoAreMarriedAtleastOne):
            continue
        if (individual[IDX_IND_DEATH] != "NA"):
            continue
        data.append("Error: INDIVIDUAL US31 " + str(individual[IDX_IND_ID]) + " named: " + individual[
            IDX_IND_NAME] + " is alive, over 30 year old and never married")
    return data


data = us31_list_living_single()
print(*data, sep="\n")
print(*data, sep="\n", file=sprint1CodeOutput)


# User story US22
# Story Name: Unique IDs
# Owner: Jyotiraditya deora (jd)
# Email: jdeora@stevens.edu
def us22_list_unique_ids(individuals, families):
    errors = []
    unique_individual_ids = set()
    unique_family_ids = set()

    # Check for unique individual IDs
    for individual in individuals:
        ind_id = individual[IDX_IND_ID]
        if ind_id in unique_individual_ids:
            errors.append(f"ERROR: US22: Duplicate individual ID {ind_id} found.")
        else:
            unique_individual_ids.add(ind_id)

    # Check for unique family IDs
    for family in families:
        fam_id = family[IDX_FAM_ID]
        if fam_id in unique_family_ids:
            errors.append(f"ERROR: US22: Duplicate family ID {fam_id} found.")
        else:
            unique_family_ids.add(fam_id)

    return errors

# Assuming 'individuals' and 'families' are lists of dictionaries
# that represent individuals and families respectively.
# IDX_IND_ID and IDX_FAM_ID are constants that represent the index or key
# for the ID in the individuals and families.

data_us22 = us22_list_unique_ids(individuals, families)
print(*data_us22, sep="\n")



# User story US38
# Story Name: List upcoming birthdays
# Owner: Jyotiraditya deora (jd)
# Email: jdeora@stevens.edu
import datetime


def us38_list_upcoming_birthdays(individuals):
    upcoming_birthdays = []
    current_date = datetime.datetime.now()
    days_in_advance = 30  # Define how many days in advance you want to check for upcoming birthdays

    for individual in individuals:
        if individual[IDX_IND_BIRTHDAY] != 'NA':
            try:
                # Extract birthday and create a date object for this year's birthday
                birth_date = datetime.datetime.strptime(str(individual[IDX_IND_BIRTHDAY]), "%Y-%m-%d").date()
                this_years_birthday = birth_date.replace(year=current_date.year)

                # Calculate the difference between today and this year's birthday
                delta = this_years_birthday - current_date.date()

                # Check if the birthday falls within the next 30 days and is not in the past
                if 0 <= delta.days < days_in_advance:
                    upcoming_birthdays.append("INFO: US38: Individual {} has an upcoming birthday on {}."
                                              .format(individual[IDX_IND_ID], this_years_birthday.strftime("%Y-%m-%d")))

            except ValueError:
                # Handle the error of incorrect data format
                upcoming_birthdays.append("ERROR: US38: Individual {} has invalid birthday date format."
                                          .format(individual[IDX_IND_ID]))

    return upcoming_birthdays


# Example usage
# Assuming 'individuals' is a list of dictionaries that represent individuals.
# IDX_IND_BIRTHDAY and IDX_IND_ID are constants that represent the index or key
# for the birthday and ID in the individuals.

data_us38 = us38_list_upcoming_birthdays(individuals)
print(*data_us38, sep="\n")


