from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

'''

    Part 1: Programming and Data Manipulation (Python)
    
'''
# 1. Data Cleaning and Preparation

# read the example csv file
example_df = pd.read_csv("data/manipulation_data.csv")
# show the first 3 rows for inspection
print(example_df.head(3))
# show some general information about the data set
print(example_df.info())

# 1.2 Identify problems
'''
    After inspection, I found the following problems:
    
    - inconsistent data format
    - missing values
    - wrong inputs
    - wrong data types
'''
# 1.3 Problems handling

# 1.3.1 inconsistent data format

# standardize missing values formate
for col, wrng_format, corr_format in zip(['Salary', 'Department'],
                                         [['not_applicable', 'not_available'], 'not_specified'],
                                         [np.nan, 'Unknown']):
    try:
        example_df[col] = example_df[col].replace(wrng_format, corr_format)
    except KeyError:
        print(f"column {col} is not in the provided df please check for spelling")

# standardize the date column and also convert to date-time object
example_df['Date_of_Birth'] = pd.to_datetime(example_df['Date_of_Birth'], errors='coerce', format='%Y-%m-%d')

# 1.3.2 wrong data types
'''
As we can see from the information displayed below that there is wrong data types and we will attempt to deal with this
by converting columns to the correct data types. for example:
    - ID column is a float64 which take a lot of memory meanwhile the ID column it self ranges form (0 to 19). so,
     may be a int8 is more suitable and more memory efficient. ofcourse the data type may vary according to the data 
     range and expected range but for this demo we will move on with int8.
     
    - Salary column an object type and needs to be converted to a numeric type may be float64
'''

# convert to numeric values
example_df['Salary'] = pd.to_numeric(example_df['Salary'], errors='coerce')

'''
     we will handle the data type of the ID column after dealing with the missing values problem, 
     because it contains np.nan which is large float number and that what makes the column's datatype float64
'''

# 1.3.3 Wrong inputs
'''
    We can see a negative value in the Salary column which does not make sense and is most probably a mistake.
    so we will ensure that all the values in the Salary column are absolute.
'''
# the target row
print(example_df.iloc[14])

# make sure every value is absolute
example_df['Salary'] = example_df['Salary'].abs()

# 1.3.4 missing values

'''
    We can see from the information displayed above that we have 9 missing values from 3 different columns which are:
        
        - ID --> 1 missing values
        - Date_of_Birth --> 4 missing values
        - Salary --> 4 missing values
        
    Strategy for handling missing values:
    
    - ID --> With only one data missing and the nature of the ID column
             (just a serial of numbers starting from 1 to number of employees) 
             we will just insert the missing data to fit the serial.
             
    - Date_of_Birth --> the missing values will be left as is, because this column is irrelevant to analysis 
                        to be performed. I did not choose to remove the rows that contains the missing values 
                        because I do not have much data.
    
    - Salary --> 4 missing values I think it's the best to fill the missing values by the average salary per department.
                 I think this will give a good approximation to missing salary values as the employees
                 in the same department have the same range of salary.
                 
'''
# examine the missing values
print(example_df.isna().sum())

# missing value for ID column
example_df.loc[4, "ID"] = 4
# change the data type of the column
example_df['ID'] = pd.to_numeric(example_df["ID"], downcast='integer')

# missing values for the salary column
# identify the department that contains the missing values
print(example_df[example_df['Salary'].isna()]['Department'])

# show the salaries of the marketing and sales departments
print(example_df[example_df['Department'].isin(['Marketing', 'Sales'])][['Salary', 'Department']])

'''
    now that we see that all salary values for the Sales department are missing, we can no longer use the average
    salary per department strategy. instead we will use the total avg of salaries for the missing values 
    for the sales department
'''

# now that we know that the 2 department with the missing values are "Sales" and "Marketing"
# let's compute the avg salary for these 2 department
avg_sales_salary = example_df['Salary'].mean()
avg_marketing_salary = example_df[example_df['Department'] == 'Marketing']['Salary'].mean()

# fill the missing values
for depart, val in zip(['Sales', 'Marketing'], [avg_sales_salary, avg_marketing_salary]):
    example_df.loc[example_df['Department'] == depart, 'Salary'] = (
        example_df.loc[example_df['Department'] == depart, 'Salary'].fillna(val))


# 1.3.5 Further inspection
'''
    now that we have dealt with all visible problems let's investigate more to see if there is other hidden problem like
    outliers and deal with them.
'''
# show stats description of the data
print(example_df.describe())

# let's inspect the number of data points that are outliers
print(example_df[example_df['Salary'] >= 1000000])

'''
    there are three points that are considered outliers, because there no much data in this data set I choose to deal
    with these outliers by capping them to the max value in each department and save them rather than just remove them.
'''

for depart in ['HR', 'Engineering']:
    # get the max values of each department excluding the outliers values
    max_val = example_df[(example_df['Department'] == depart) & (example_df['Salary'] < 1000000)]['Salary'].max()

    # Cap the salary at max_val for outliers in the department
    example_df.loc[(example_df['Department'] == depart) & (example_df['Salary'] >= 1000000), 'Salary'] = max_val

# export the cleand file
example_df.to_csv("data/manipulation_data_cleaned.csv")

# 2. Data Analysis and Aggregation

# 2.1 Calculate the average salary per department
avg_per_depart = example_df.groupby("Department")["Salary"].mean()

# 2.1 Find the top 3 highest paid employees
top_3_paid_employee = example_df.nlargest(3, 'Salary')

# 2.1 Determine the number of employees in each department
employee_count_df = example_df['Department'].value_counts()


# 3. API utilization

app = Flask(__name__)


@app.route('/top_n_employees', methods=['GET'])
def top_n_employees():
    # Get the 'n' parameter from the request
    n = int(request.args.get('n', 5))  # Default to top 5 if 'n' is not provided

    # Get the top N highest-paid employees
    top_n = example_df.nlargest(n, 'Salary')[['Name', 'Salary', 'Department']]

    # Convert the result to a list of dictionaries and return as JSON
    result = top_n.to_dict(orient='records')
    return jsonify(result)


@app.route('/employee_count', methods=['GET'])
def employee_count():
    # Get the 'department' parameter from the request
    department = request.args.get('department', None)

    if department is None:
        return jsonify({'error': 'Department parameter is required'}), 400

    # Calculate the number of employees in the given department
    count = example_df[example_df['Department'] == department].shape[0]

    # Return the count as JSON
    return jsonify({'department': department, 'employee_count': count})


if __name__ == '__main__':
    app.run(debug=True)
