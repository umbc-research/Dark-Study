import glob
import sys
import pandas as pd
from astropy.io import fits
from matplotlib import pyplot as plt
import numpy as np
import tqdm


def open_files(folder_path):
    #Load all files from the folder into a list
    fits_files = glob.glob(folder_path + '**\\*.fits', recursive=True)
    stats = {"Type" : [], "Integration Time": [],"Camera":[], "Mean":[], "Median": [], "Standard Dev." : [],"Gain": []}

  #Fill the dict with all the needed header information
    for file in tqdm.tqdm(fits_files):

        hdu = fits.open(file)
        header = hdu[0].header

        frame_width = header["NAXIS1"]
        width_cropmargin = int(frame_width * .1)
        frame_height = header["NAXIS2"]
        height_cropmargin = int(frame_height * .1)
        y = frame_height - height_cropmargin
        x = frame_width - width_cropmargin
        data = hdu[0].data[height_cropmargin:y,width_cropmargin:x]  
        mean, median , std = np.average(data), np.median(data), np.std(data)

        if 'OBJECT' in header:
            stats["Type"].append("DomeDarks")
        else:
            stats["Type"].append("BoxDarks")       
        
        stats["Camera"].append(header["INSTRUME"])
        stats["Gain"].append(header["GAIN"])
        stats['Integration Time'].append(header["EXPTIME"])
        stats['Mean'].append(mean)
        stats['Median'].append(median)
        stats['Standard Dev.'].append(std)

    #convert dict into Pandas Dataframe
    df = pd.DataFrame(stats)
    #If data frame needs to be displayed use these lines and print(df)
    #pd.set_option('display.max_rows', None) 
    #pd.set_option('display.max_columns', None)

    return df

def mean_comparison_satterplot(df):
    
    #Seperate Box Darks and Dome Darks to graph 
    BoxDarks = df[df['Type'] == 'BoxDarks']
    DomeDarks = df[df['Type'] == 'DomeDarks']

    #Group the Each Dark varient by the integration time and gain then take the mean of the groups
    DD_error = DomeDarks.groupby(['Type','Integration Time','Gain'])['Mean'].std().to_list()
    BD_error  = BoxDarks.groupby(['Type','Integration Time','Gain'])['Mean'].std().to_list()
    DD_error = [x / 10 for x in DD_error]
    BD_error = [x / 10 for x in BD_error]

    #Create 2 new dataFrames each holding the mean of the frames in each group
    DomeDarks = DomeDarks.groupby(['Type','Integration Time','Gain'])['Mean'].mean().reset_index()
    BoxDarks = BoxDarks.groupby(['Type','Integration Time','Gain'])['Mean'].mean().reset_index()
    
    Dome_means = [mean for mean in DomeDarks['Mean']]
    Box_means = [mean for mean in BoxDarks['Mean']]

    color = [
    'b' if time <= 1 else
    'teal' if time <= 5 else
    'orange' if time <= 15 else
    'red' if time > 15 else
    'black' for time in DomeDarks['Integration Time']
]



    Box_gain = [cam for cam in BoxDarks['Gain']]

    for i in range(len(Box_gain)):
        if Box_gain[i] == 0:
            mk = '*'
        elif Box_gain[i] <= 50:
            mk = 'o'
        elif Box_gain[i] <= 200:
            mk = '^'
        else:
            mk = 'x'
        

        plt.scatter(Box_means[i],Dome_means[i],marker=mk,c=color[i])
        plt.yscale('log')
        plt.xscale('log')
        plt.grid(1)
    max_val = max(max(Box_means), max(Dome_means))
    x = np.linspace(0, max_val,100)
    plt.plot(x,x,label='1:1 Line')

    plt.title("Dome vs Box Dark Mean Frame Count Comparison(ASI 432mm)")
    plt.xlabel("Box Dark Mean Frame count")
    plt.ylabel("Dome Dark Mean Frame count")

    plt.show()

    
        
def median_comparison_scatterplot(df):
        #end goal have two frames with medians of medians standard error 
    BoxDarks = df[df['Type'] == 'BoxDarks']
    DomeDarks = df[df['Type'] == 'DomeDarks']

    DD_error = DomeDarks.groupby(['Type','Integration Time','Gain'])['Median'].std().to_list()
    BD_error  = BoxDarks.groupby(['Type','Integration Time','Gain'])['Median'].std().to_list()

    DD_error = [x / 10 for x in DD_error]
    BD_error = [x / 10 for x in BD_error]

    DomeDarks = DomeDarks.groupby(['Type','Integration Time','Gain'])['Median'].mean().reset_index()
    BoxDarks = BoxDarks.groupby(['Type','Integration Time','Gain'])['Median'].mean().reset_index()

    Dome_medians = [median for median in DomeDarks['Median']]
    Box_medians = [median for median in BoxDarks['Median']]

    color = [
    'b' if time <= 1 else
    'teal' if time <= 5 else
    'orange' if time <= 15 else
    'red' if time > 15 else
    'black' for time in DomeDarks['Integration Time']
]



    Box_gain = [cam for cam in BoxDarks['Gain']]

    for i in range(len(Box_gain)):
        if Box_gain[i] == 0:
            mk = '*'
        elif Box_gain[i] <= 50:
            mk = 'o'
        elif Box_gain[i] <= 200:
            mk = '^'
        else:
            mk = 'x'
        

        plt.scatter(Box_medians[i],Dome_medians[i],marker=mk,c=color[i])
        plt.yscale('log')
        plt.xscale('log')
        plt.grid(1)
    max_val = max(max(Box_medians), max(Dome_medians))
    x = np.linspace(0, max_val,100)
    plt.plot(x,x,label='1:1 Line')

    plt.title("Dome vs Box Dark Median Frame Count Comparison(ASI 432mm)")
    plt.xlabel("Box Dark Median Frame count")
    plt.ylabel("Dome Dark Median Frame count")

    plt.show()




if __name__ == "__main__":

    stattype = sys.argv[1] 
    folder_path = sys.argv[2] 
    df = open_files(folder_path)
    if(stattype.lower() == 'mean'):
        mean_comparison_satterplot(df)
    else:
        median_comparison_scatterplot(df)
