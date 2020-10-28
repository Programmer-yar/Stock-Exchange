""" Verified for correct results. It is working
But database objects should be passed from view function """


from .models import File, Company
import csv
from io import StringIO

def Result_func(volume, three_files, five_files, hundred_files):
    reference_volume = volume 
    three_files = three_files
    hundred_files = hundred_files
    five_files = five_files
    

    filtered_companies_name = TotalVolume(three_files, reference_volume)
    moving_avg = MovingAverage(filtered_companies_name, hundred_files)
    final_data = ClosingsAverage(moving_avg, five_files)
    crossings = CrossingsCheck(final_data)
    crossings_list = CrossingsToList(crossings)

    # database = [three_files, five_files, filtered_companies_name, moving_avg,
    #             final_data, crossings]  
    return crossings_list
    



def TotalVolume(three_files, reference_volume):
    """ This function calculates total volume of companies for previous 3 days """
    reference_volume = reference_volume
    company_volume = []
    filtered_companies = []
    filtered_companies_name = []

    count=1
    for file in three_files:
        if count == 1:
            for company in file.company_set.all():
                company_volume.extend([company.symbol, company.volume])
            count += 1
        else:
            for company in file.company_set.all():
                if company.symbol in company_volume:
                    index = company_volume.index(company.symbol)
                    index += 1
                    company_volume[index] = company_volume[index] + company.volume
                else:
                    company_volume.extend([company.symbol, company.volume])

    for index in range(1, len(company_volume), 2):
        if company_volume[index] > reference_volume:
            company_symbol = company_volume[index-1]
            filtered_companies.extend([company_symbol, company_volume[index]])
            filtered_companies_name.append(company_symbol) 

    return filtered_companies_name



def MovingAverage(filtered_companies_name, hundred_files):
    """ Calculates moving avg of companies provided as argument """
    """ pass 100 files here when database loaded """
    """ This function will take most of processing time """
    closing_price = []
    moving_avg = []
    

    for file in hundred_files:
        for company in file.company_set.all():
            if company.symbol in filtered_companies_name:
                if company.symbol in closing_price:
                    index = closing_price.index(company.symbol)
                    index += 1
                    closing_price[index] = closing_price[index] + company.closing
                    index += 1
                    closing_price[index] += 1
                else:
                    closing_price.extend([company.symbol, company.closing, 1])

    for num in range(1, len(closing_price), 3):
        avg = closing_price[num]/closing_price[num+1]
        avg = round(avg, 2)
        moving_avg.extend([closing_price[num-1], avg])

    return moving_avg


def ClosingsAverage(moving_avg, five_files):
    """ Takes the moving_avg of filtered companies and stores them in a dictionary
    alongwith their current and previous closings """
    """ Pass previous 20 dates here when database loaded
    else the previos closing may be missed which will cause error in next function  """
    final_data = {}
    for count in range(0, len(moving_avg), 2):
        final_data[moving_avg[count]] = {'moving_avg':moving_avg[count+1]}


    for file in five_files:
        for company in file.company_set.all():
            if company.symbol in moving_avg:
                if 'current_closing' in final_data[company.symbol]:
                    if 'status' not in final_data[company.symbol]:
                        final_data[company.symbol]['previous_closing'] = company.closing
                        final_data[company.symbol]['status'] = True
                else:
                    final_data[company.symbol]['current_closing'] = company.closing

    
    deletion_keys = []
    for company, closings in final_data.items():
        if 'previous_closing' not in closings:
            deletion_keys.append(company)

    for key in deletion_keys:
        del final_data[key]


    return final_data

def CrossingsCheck(final_data):
    """ This function takes moving_avg, current and previous closings of filtered
    companies and analyze their data to check for crossings """
    crossings = {}

    for company, closings in final_data.items():
        move_avg = closings['moving_avg']
        current = closings['current_closing']
        previous = closings['previous_closing']

        if move_avg > current and move_avg < previous:
            crossings[company] = {'down':round((current-move_avg), 2), 'moving_avg':move_avg}
        elif move_avg < current and move_avg > previous:
            crossings[company] = {'up':round((current-move_avg), 2), 'moving_avg':move_avg}

    return crossings



def CrossingsToList(crossings):
    crossings_list = []

    for company, closing in crossings.items():
        temp_list = []
        temp_list.append(company)

        for key, val in closing.items():
            temp_list.append(val)

        crossings_list.append(temp_list)

    return crossings_list



def files_to_database(file):


    files_list = []
    files_list.append(file)

    rejected_files = []
    already_files = []
    all_files = File.objects.all()
    for file in all_files:
        already_files.append(str(file.file_name)) #Stores already present file names

    for num in range(1): #len(files_list)
        


        file_title = str(files_list[num]).replace('.txt', '')

        if file_title not in already_files:
            csvfile = files_list[num].read().decode('utf-8')
            file_object = File.objects.create(file_name=file_title)
            print('opened:', files_list[num])
            csvreader = csv.reader(StringIO(csvfile), delimiter=',')
            fields = next(csvreader) #Here used to eliminate header in csv files  
            print(100*'*','\n')
            
            for each_row in csvreader:
                Company.objects.create(file_name=file_object, symbol=each_row[0],
                                       closing=float(each_row[5]), volume=int(each_row[6]))

            

        else:
            name = str(files_list[num]) + '.txt'
            rejected_files.append(name)
            print(f'File with name {files_list[num]} already present')

    return rejected_files