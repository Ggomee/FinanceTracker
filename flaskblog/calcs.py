import pandas as pd
import numpy as np
import datetime as dt

def sample_calc(starting_year, starting_value):
    i=0
    value_list=[starting_value]
    year_list=[starting_year]
    rng=5
    for i in range(rng):
        value_next=value_list[i]*1.03
        year_next=year_list[i]+1
        i+1
        value_list.append(value_next)
        year_list.append(year_next)
    df=pd.DataFrame()
    df['year']=year_list
    df['values']=value_list
    return df

def print_tables(post, details):
    print(post)
    print(details)
    return 0

def monthly_r(r):
   r2= np.power((1+r),(1/12))-1
   return r2

def zerolistmaker(n):
    listofzeros = [0] * n
    return listofzeros

#def main_calc(start_age, start_date, scenario_name, inflation, withdrawal_rate, df)
#function will take in fields from posts table and the table of data. Returns a df


def main_calc(start_year, start_month, inflation, withdrawal_rate, start_age, retirement_age, df):


    start_age=start_age
    rng=retirement_age-start_age   #this sets charts and everything. eventually move to avg lifespan of someone?
    start_date=dt.datetime(start_year,start_month, 1)
    inflation=inflation/100
    withdrawal_rate=withdrawal_rate/100
    df = df

    df['act_date'] = pd.to_datetime(
        df.date_entry_year.astype(int).astype(str) + '-' + df.date_entry_month.astype(int).astype(str) + '-1',
        format='%Y-%m')

    account_value={}
    for x in range(len(df['item_id'])):
        loop_entry_name = df['entry_name'].reset_index(drop=True)[x]
        account_value['Acct' + loop_entry_name]=zerolistmaker(rng+1)

    for x in range(len(df['item_id'])):
       loop_date=pd.to_datetime(start_date) #Main dates in question starting at start date
       loop_act_date=pd.to_datetime(df['act_date'].reset_index(drop=True)[x]) # date of new entry
       loop_contrib = df['contrib'].reset_index(drop=True)[x]
       loop_perc_change = df['perc_change'].reset_index(drop=True)[x]
       loop_entry_name = df['entry_name'].reset_index(drop=True)[x]
       loop_value = df['value'].reset_index(drop=True)[x]

       loop_date_list=[loop_date]
    #   account_value['Acct' + loop_entry_name]=zerolistmaker(rng+1)
    ######DO I NEEED ANYMORE
       try:
           account_value['Acct' + loop_entry_name]
           j=0

       except KeyError:
           account_value['Acct' + loop_entry_name][0] = [loop_value]

       for j in range(rng):

           if loop_act_date == loop_date_list[j]:  # if the data listed in table = actual date then use the date in table
               account_value['Acct' + loop_entry_name][j] = loop_value
    #       else loop_act_date > loop_date_list[j]:   # if the date in table is greater than use the old value that's in the system this is
    #           account_value['Acct' + loop_entry_name][j] = account_value['Acct' + loop_entry_name][j]

           else:
               account_value['Acct' + loop_entry_name][j]=account_value['Acct' + loop_entry_name][j]

           next_loop_value=account_value['Acct' + loop_entry_name][j]*(1+monthly_r(loop_perc_change))+loop_contrib
           next_loop_date = (loop_date_list[j] + pd.DateOffset(months=1)).date() # next normal date

           account_value['Acct' + loop_entry_name][j+1]=next_loop_value
           loop_date_list.append(next_loop_date)

    df_accounts=pd.DataFrame(account_value)
    df_accounts['Net Worth'] = df_accounts.sum(axis=1)
    df_accounts['Dates']=loop_date_list

    return df_accounts

