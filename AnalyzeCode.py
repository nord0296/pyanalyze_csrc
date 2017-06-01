
# for code analysis
import lizard

# for directory / file traversing
from os import makedirs
from os.path import isfile, join, splitext, basename, exists
from os import walk

TreesToAnalyze = [
    "..\..\Modules", # modules root
    "..\..\src" # app layer
]

ExtensionsToAnalyze = [
    ".c",
    # ".h"
]

ResultDir = "./Reports/"
SummaryReport = "__SummaryByFile.csv"


Result_List = []
LogFile = None

def AnalyzeFile(filename):
    # takes a path to a file and analyzes it.  We currently only analyze *.h and *.c files, so this will check that
    # and do nothing if the extension doesn't match
    file_name, file_extension = splitext(filename)

    if( file_extension in ExtensionsToAnalyze ):
        i = lizard.analyze_file(filename)
        Result_List.append(i.function_list)
        print filename + " has been analyzed"

def AnalyzeDirectory(dir):
    # takes a directory path to analyze and looks at each *.c file inside
    # recursively calls itself anytime it finds a directory inside.
    print dir + " is being analyzed"
    for root, dirs, files in walk(dir, topdown=True):
        for fname in files:
            AnalyzeFile( join(root, fname) )
        #for dname in dirs:
        #    AnalyzeDirectory( join(root, dname) )


def DumpModuleReport( func_list ):
    f = None
    idx = 0
    for func in func_list:
        #increment function index, this may already be in the dictionary too...
        idx += 1

        if f is None:
            # get name for log and open it if it doesn't exist yet (None)
            full_fname = func.filename
            logname = basename(full_fname)
            logname += ".csv"
            f = open(ResultDir + logname, "w")
            f.write("Function Number, Cyclomatic complexity, Lines of code\n")

        #write the data
        f.write(str(idx) + "," +
                str(func.cyclomatic_complexity) + "," +
                str(func.nloc) +
                "\n")

    if f is not None:
        f.close()

def DumpResultsToCSV( list ):
    # this is a list of lizard function_list objects
    # function list has many fields, examples:
    #   cyclomatic_complexity
    #   token_count
    #   name (without arguments)
    #   parameter_count
    #   nloc
    #   long_name (prototype)
    #   start_line

    # we want a few things from our CSV files:
    #   module_name.c, total complexity, total nloc
    #
    #
    f = open(ResultDir + SummaryReport, "w")
    f.write( "Filename, Number of Functions, total cyclomatic complexity, total lines of code\n" )
    for module_func_list in list:

        if len(module_func_list) > 0:
            # calc total complexity and nloc
            total_complexity = 0
            total_nloc = 0
            num_funcs = 0
            for func in module_func_list:
                full_fname = func.filename
                total_complexity += func.cyclomatic_complexity
                total_nloc += func.nloc
                num_funcs += 1

            # only report the filename without extension
            fname = basename(full_fname)

            # output the data and move on to the next module.
            f.write(fname + "," + str(num_funcs) + "," + str(total_complexity) + "," + str(total_nloc) + "\n")

    f.close()

    # next, we also want to create defailts for each module
    #   let's assume we will use modulename_report.csv
    for module_func_list in list:
        DumpModuleReport( module_func_list )



def main():
    # main function called in script

    # create report directory if it does not exist
    if not exists(ResultDir):
        makedirs(ResultDir)

    for dir in TreesToAnalyze:
        AnalyzeDirectory(dir)

    # once here we have a list of results stored in Result_List
    #   Dump it to a CSV...
    DumpResultsToCSV( Result_List )

if __name__ == '__main__':
    main()