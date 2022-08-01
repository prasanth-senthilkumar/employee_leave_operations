import sys, re
import csv
from datetime import datetime, date, timedelta

class EmployeeLeave:

    PUBLIC_HOLIDAYS = ('26/01/2022','15/04/2022','15/08/2022')
    LEAVE_TYPE = ("OOO(Out Of Office)",)
    headers = []

    def __init__(self, emp_id, csv_file):
        self.emp_id = emp_id
        self.file_name = csv_file
        self.leaves_applied = []

    def get_employee_data(self):
        """Gets employee details from the CSV file"""
        employee_leave_data = {}

        try:
            # Reading employee details from CSV
            with open(self.file_name) as file_reader:
                read_data = csv.DictReader(file_reader, delimiter = ',')
                count = 1
                for row in read_data:
                    employee_leave_data[count] = row
                    if not self.headers: 
                        for key in row.keys(): self.headers.append(key)
                    count+=1
            return employee_leave_data
        except Exception as e:
            print ("ERROR: Failed to read employee data from CSV. {}".format(e))
            return 0

    def apply_leave(self):
        """Applies leave and updates the CSV file with remaining leaves"""
        date_start, date_end = '',''
        date_start_obj, date_end_obj = '',''
        dd_start,mm_start,yy_start,dd_end,mm_end,yy_end = '','','','','',''
        attempt_leave_type, attempt_max_start, attempt_max_end = 3,3,3
    
        count = 1
        while attempt_leave_type > 0:
            print("Please enter the number corresponding to the type of leave you wish to opt for")
            for type in self.LEAVE_TYPE:
                print ("{}- {}".format(count,type))
                count+=1
            try:
                leave_type_choice = int(input("Your choice: "))
                if leave_type_choice > len(self.LEAVE_TYPE) or leave_type_choice < 1:
                    raise Exception("Invalid entry selected. Please try again")
            except Exception as e:
                print ("Please enter a valid choice (in number)",e)
                attempt_leave_type -= 1
                print ("Remaining attempts: {}".format(attempt_max_end))
                continue
            break

        if attempt_leave_type <= 0: print ("Reached maximum number of attempts\n\n"); sys.exit()
    
        # Validate the start date entered
        while attempt_max_start > 0:
            date_start = str(input("Please enter the start date of the leave in format dd/mm/yyyy: "))
            print ("Entered START date: {}".format(date_start))
            try:
                dd_start,mm_start,yy_start = date_start.split('/')
                date_start_obj = datetime(year=int(yy_start),month=int(mm_start),day=int(dd_start))
                if int(yy_start) < 2022 or int(yy_start) > 2022:
                    raise Exception("ERROR: Leaves can be applied for dates only in this year (2022). Please enter a date in this year.")
            except:  
                print ("Error: Entered START date is not valid. Please enter a valid date in format dd/mm/yyyy.\n")
                attempt_max_start -= 1
                print ("Remaining attempts: {}".format(attempt_max_start))
                continue
            break
        if attempt_max_start <= 0: print ("Reached maximum number of attempts\n\n");sys.exit()
    
        # Validate the end date entered
        while attempt_max_end > 0:
            date_end = str(input("Please enter the end date of the leave in format dd/mm/yyyy: "))
            date_validated = 0
            print ("Entered END date: {}".format(date_end))
            try:
                dd_end,mm_end,yy_end = date_end.split('/')
                date_end_obj = datetime(year=int(yy_end),month=int(mm_end),day=int(dd_end))
            except:
                print ("Error: Entered END date is not valid. Please enter a valid date in format dd/mm/yyyy.\n")
                attempt_max_end -= 1
                print ("Remaining attempts: {}".format(attempt_max_end))
                continue
    
            if date_start_obj > date_end_obj:
                print ("ERROR: End date should be the same or after the start date. Please enter a valid end date.")
                attempt_max_end -= 1
                print ("Remaining attempts: {}".format(attempt_max_end))
                continue
            break
        if attempt_max_end <= 0: print ("Reached maximum number of attempts\n\n");sys.exit()

        # Get the list of days in between
        start_date = date(int(yy_start), int(mm_start), int(dd_start)) 
        end_date = date(int(yy_end), int(mm_end), int(dd_end))
        delta = end_date - start_date
        list_of_days = []
        for delta_days in range(delta.days + 1):
            day = start_date + timedelta(days=delta_days)
            list_of_days.append(day.strftime("%d/%m/%Y"))

        # Exclude weekends and public holidays
        leave_days = len(list_of_days)
        weekend_count = 0
        for day in list_of_days:
            dd,mm,yy = re.search("(\d+)/(\d+)/(\d+)",day).group(1,2,3)
            date_check_workday = datetime(year=int(yy),month=int(mm),day=int(dd))
            if day in self.PUBLIC_HOLIDAYS:
                print ("There is a public holiday in the given date range {}".format(day))
                leave_days -= 1
            elif date_check_workday.weekday() > 4:
                weekend_count += 1
                leave_days -= 1
    
        if weekend_count: print ("Number of weekends in the given date range is {}".format(weekend_count))
        if leave_days < 0: leave_days = 0

        print ("Number of actual days for this leave request is {} days".format(leave_days))
    
        # If leave request days is 0 don't raise the request
        if leave_days <= 0:
            print ("As the number of actual days for this leave request is {} days, this leave request cannot be raised\n\n".format(leave_days))
            return 0

        # Check if there are sufficient number of leaves
        available_leave = self.check_leave_balance()
        if available_leave < leave_days: 
            print ("ERROR: Number of leaves required for this request ({}) is lesser than then number of available leaves ({}).\nPlease try again.\n\n".format(leave_days,available_leave))
            return 0
    
        # Check if there are any existing leave requests with overlapping dates
        if self.leaves_applied:
            existing_list_of_days = []
            for date_range in self.leaves_applied:
                dd1,mm1,yy1 = re.search("Start date: (\d+)/(\d+)/(\d+)",date_range[0]).group(1,2,3)
                dd2,mm2,yy2 = re.search("End date: (\d+)/(\d+)/(\d+)",date_range[1]).group(1,2,3)
                start_date1 = date(int(yy1), int(mm1), int(dd1)) 
                end_date1 = date(int(yy2), int(mm2), int(dd2))
                delta1 = end_date1 - start_date1
    
                for iteration in range(delta1.days + 1):
                    day1 = start_date1 + timedelta(days=iteration)
                    existing_list_of_days.append(day1.strftime("%d/%m/%Y"))
    
                data_overlap = [data for data in existing_list_of_days if data in list_of_days]
                if data_overlap:
                    print ("ERROR: Leave request for one or more dates in the given date range is already applied. ".format(date_range))
                    print ("Overlapping days {}".format(data_overlap))
                    print ("Please enter valid date range for the leave request\n")
                    return 0

        # If success store the leave data
        self.leaves_applied.append(["Start date: {}".format(date_start), "End date: {}".format(date_end), "Total leave days: {}".format(leave_days), "Leave type: {}".format(self.LEAVE_TYPE[leave_type_choice-1])])

        updated = self.update_employee_leave_details(self.check_leave_balance()-leave_days)
        if not updated: sys.exit()
        print ("\nSuccessfully raised a leave request and the leave balance is updated.")
        print ("Updated leave balance is {}\n\n".format(self.check_leave_balance()))
    
    def check_leave_balance(self):
        """Gets and returns the leave balance from CSV data for the employee"""
        employee_leave_data = self.get_employee_data()
        if not employee_leave_data:
            print ("ERROR: Failed to check employee leave balance")
            return 0
        leave_balance = ''
        for key in employee_leave_data.keys():
            data = employee_leave_data[key]
            if data['EmpId'] == self.emp_id:
                return int(data['LeaveBalance'])

    def cancel_leave(self):
        """Cancels a leave request and updates the leave balance in CSV"""
        # Return if there are no existing leave requests
        if not self.leaves_applied:
            print ("There are no existing leave requests to cancel\n\n")
            return 0

        print ("Please select the leave request to cancel from the below list")
        count = 1
        print ("0- Exit")
        for leave in self.leaves_applied:
            print ("{}. {}".format(count,leave))
            count+=1
        try:
            choice = int(input("Enter your choice: "))
        except:
            print ("Please enter a valid choice")
        if choice == 0: return
        if choice > len(self.leaves_applied) or choice < 0:
            print ("Please select a valid entry (1-{})".format(len(self.leaves_applied)))
            return 0
        leave_to_cancel = self.leaves_applied[choice-1]
        self.leaves_applied.remove(leave_to_cancel)

        # Update the leave balance in CSV
        leave_balance_to_add = re.search("Total leave days: (\d+)",leave_to_cancel[2]).group(1)
        updated = self.update_employee_leave_details(self.check_leave_balance()+int(leave_balance_to_add))
        if not updated: sys.exit()
        print ("\nSuccessfully cancelled leave request and updated the leave balance.")
        print ("Updated leave balance is {}\n\n".format(self.check_leave_balance()))

    def update_employee_leave_details(self, leave_balance):
        """Updates employee leave balance in CSV"""
        employee_leave_data = self.get_employee_data()
        if not employee_leave_data:
            print ("ERROR: Failed to update employee leave details")
            return 0
        for key in employee_leave_data.keys():
            data = employee_leave_data[key]
            if data['EmpId'] == self.emp_id:
                data['LeaveBalance'] = leave_balance
                if self.leaves_applied: data['AppliedLeaves'] = self.leaves_applied
                employee_leave_data[key] = data
        try:
            with open(self.file_name, 'w') as file_writer:
                write_csv = csv.DictWriter(file_writer, delimiter = ',', fieldnames = self.headers, lineterminator='\n')
                write_csv.writeheader()
                for key in employee_leave_data.keys():
                    write_csv.writerow(employee_leave_data[key])
        except Exception as e:
            print ("Failed to update employee leave details in CSV. {}".format(e))
            return 0
        return 1

    def check_leaves_applied(self):
        """Displays employee leave details"""
        count = 1
        if self.leaves_applied:
            for leave in self.leaves_applied:
                print ("{}. {}".format(count, leave))
                count += 1
            print ("\n\n")
        else:
            print ("There are no leaves applied yet\n\n")

    def get_name(self):
        """Get and return employee naem for the given employee id from the CSV"""
        employee_leave_data = self.get_employee_data()
        if not employee_leave_data:
            print ("ERROR: Failed to check employee data")
            return 0
        for key in employee_leave_data.keys():
            if employee_leave_data[key]['EmpId'] == self.emp_id: return employee_leave_data[key]['Name']
        return 0


# Operation starts here
csv_file = r"EmployeeDataLeaves.csv"
emp_id = str(input("Please enter your employee id: "))
emp_obj = EmployeeLeave(emp_id, csv_file)

# Check if employee id is present in database
name = emp_obj.get_name()
if name:
    print ("Welcome {}!!".format(name))
else:
    print ("ERROR: No employee found for the given employee ID in database. Please enter a valid Employee ID\n")
    sys.exit()

choice = 1
while choice != 5:
    print ("1. Apply leave\n2. Check leave balance\n3. Cancel leave\n4. Check leaves applied\n5. Exit")
    choice = str(input("Please enter your choice: "))
    print ("Your choice is {}".format(choice))

    if choice == '1':
        success = emp_obj.apply_leave()
        if not success:
            continue
    elif choice == '2':
        print ("Your leave balance is {} days\n\n".format(emp_obj.check_leave_balance()))
    elif choice == '3':
        emp_obj.cancel_leave()
    elif choice == '4':
        emp_obj.check_leaves_applied()
    elif choice == '5':
        break
    else:
        print ("Please enter a valid option (1-4): ")
