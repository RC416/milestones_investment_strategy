# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 21:12:50 2019
Define milestone class
@author: Ray
"""

import pandas as pd
import numpy as np
import random

pd.set_option('display.max_columns',15)
pd.set_option('display.width', 200)

class Milestone:
    def __init__(self, events, value, timing, probabilities=None, outcomes=None, upfront_timing=0):
        self.events = events
        self.value = value
        self.timing = timing
        self.outcomes = outcomes
        self.upfront_timing = upfront_timing
        self.data = pd.DataFrame({'events':events,'value':value,'timing':timing, 
                                  'probabilities':probabilities, 'evs':None, 'outcomes':outcomes,
                                  'payouts':None, 'NPV':None, 'NPV evs':None})
        
        self.data['payouts'] = self.data['outcomes'] * self.data['value']
        self.data['evs'] = self.data['probabilities'] * self.data['value']
        
        self.face_value = self.data['value'].sum()
        
    def valuation(self, discount_rate=0.10, outcomes=None):
        
        # updates outcomes if you want to input new outcomes
        # more efficient for looking at many outcome scenarios        
        if outcomes != None:
            self.data['outcomes'] = outcomes
            self.data['payouts'] = self.data['outcomes'] * self.data['value']
        
        #calculates NPV, multiple, IRR and cash flows
        def calculate_npv(self, discount_rate):
            
            #calculate npv of each milestone and sum
            def calculate_npv(milestone_df):
                payout = milestone_df['payouts']
                timing = milestone_df['timing']
                return payout / ((1 + discount_rate) ** (timing))     
            
            self.data['NPV'] = self.data.apply(calculate_npv, axis=1)
                    
            #calculate npv and multiple
            self.npv = self.data['NPV'].sum()   
                    
            def calculate_npv_evs(milestone_df):
                payout = milestone_df['evs']
                timing = milestone_df['timing']
                return payout / ((1 + discount_rate) ** (timing))   
            
            self.data['NPV evs'] = self.data.apply(calculate_npv_evs, axis=1)        
            
        def calculate_multiple(self):
            self.payout = self.data['payouts'].sum() 
            self.upfront = self.data['NPV evs'].sum()
            self.multiple = self.payout / self.upfront
    
        def cash_flows(self):
            # output non-zero payouts into df
            self.cash_flows = self.data.loc[self.data['outcomes'] != 0, ('timing', 'payouts')]
            # add upfront payment at timing=0
            upfront = self.data['NPV evs'].sum()
            self.cash_flows = self.cash_flows.append({'timing':self.upfront_timing, 'payouts':-upfront}, ignore_index=True)
            self.cash_flows.sort_values(by=['timing'], inplace=True)
            
        def calculate_irr(self): # IRR separated since it's a bit more complicated
            
            # define a funciton to process payouts/timing and calculate IRR
            # currently does not handle differnt upfront timing
            def irr(payouts, timing, upfront):
                # create time points up to the last one in the timing 
                timeline = list(range(1,max(timing)+1))
                cash_flows = []
                cash_flows.append(-upfront)
        
                for time in timeline:
                    # check if there is a payout at each time point & append payout
                    if time in timing:
                        index = timing.index(time)
                        cf = payouts[index]
                        cash_flows.append(cf)
                    else:
                        cash_flows.append(0)
        
                return np.irr(cash_flows)
            
            # calculate normal IRR according to payouts defined by outcomes
            payouts = self.data['payouts'].tolist()
            timing = self.data['timing'].tolist()
            upfront = self.data['NPV evs'].sum()
            
            self.irr = irr(payouts, timing, upfront)
            
            # calculate 'expected' IRR according to expected milestone values            
            expected_payouts = self.data['evs'].tolist()
            
            self.expected_irr = irr(expected_payouts, timing, upfront)
            #
        
        # runs each function to calculate key financial metrics
        calculate_npv(self, discount_rate)
        calculate_multiple(self)
        cash_flows(self)
        calculate_irr(self)

         
# function to convert stage success probabilities to cumulative
stage_prob = [0.320, 0.632, 0.307, 0.496]

def cumulative_probs(probabilities):
    cumulative_probabilities = []
    probs = probabilities[:] # create a shallow copy so input list is not mofidied
    probs.append(0)
    
    for p in range(1, len(probs)):
        c_prob = np.prod(probs[:p]) * (1-probs[p])
        cumulative_probabilities.append(c_prob)
    
    return cumulative_probabilities
'''
each output probability reflects the probability of achieving exactly that stage
i.e. 32% chance of successing from preclinical to phase 1 => sum of probabilities phase 1 and beyond is 32%

the cumulative probability for stage n is:
    x1 * x2 * x3 ... * x(n-1) * (1 - xn)
the funciton calculates this value for each stage based on the 
probability of success at each stage

c_prob = (probability of getting to stage) x (prob not advancing)
new list is created as to not modify input
0 is appended to signify 0% prob of advancing beyond last stage

# test values
print(cumulative_probs(stage_prob))
print(cumulative_probs([0.5, 0.5, 0.5, 0.5]))
print(cumulative_probs([1,0]))
print(cumulative_probs([1,1,1,1,1]))
'''


# convert dataframe of Cfs to list with blanks for years w/o payment
def portfolio_cfs(cash_flows):
    # sums cashflow and groups for each year
    grouped_table = cash_flows.groupby(['timing']).sum().reset_index()
    # creates timeline and collects times of payments
    timeline = list(range(0, int(grouped_table['timing'].max()) + 1))
    
    # pull out timing and cfs from the dataframe. Convert to INT for timing
    timing = [round (x) for x in grouped_table['timing'].tolist()]
    cf_list = grouped_table['payouts'].tolist()
    
    total_cf = [] # list to capture cash flows plus blank years
    
    for time in timeline:
        if time in timing:
            index = timing.index(time)
            cf = cf_list[index]
            total_cf.append(cf)
            
        else:
            total_cf.append(0)       
  
    return total_cf  
'''
The milestone class outputs a df with cash flows and timings
This function converts that df to a list for calculating irr and plotting
for years without a payment, it fills in blank values

test values: 
cf_df = pd.DataFrame({'timing': [0,1,3], 'payouts':[-25,32,12]})
cfs = portfolio_cfs(cf_df)
irr = np.irr(cfs) # irr = 49%
'''


# create outcome scenarios depending on how many milestones remain
def generate_outcome(n_events, stage_probs):
    
    prob_list = stage_probs[-n_events:]
    prob_list = cumulative_probs(prob_list)
    prob_list.insert(0, 1 - sum(prob_list))
    
    outcome_scenarios = {
        '2': [[0,0],[1,0],[1,1]],
        '3': [[0,0,0],[1,0,0],[1,1,0],[1,1,1]],
        '4': [[0,0,0,0], [1,0,0,0], [1,1,0,0], [1,1,1,0], [1,1,1,1]]
        }
    
    choice = random.choices(range(n_events+1), weights=prob_list, k=1)
    outcome = outcome_scenarios[str(n_events)][choice[0]]
    return outcome




'''
# some values for testing Milestone class
events = ['phase 1', 'phase 2', 'phase 3', 'approval']
value = [10, 20, 50, 100]
timing = [1, 3, 5, 7]
cumulative_probabilities = [0.11, 0.14, 0.03, 0.03]
outcomes = [1, 1, 0, 0]

# initialise and call valuation methods
test_milestone = Milestone(events, value, timing, cumulative_probabilities, outcomes)
test_milestone.valuation(discount_rate=0.15, outcomes=outcomes)

test_data = test_milestone.data
print(test_data)

print('irr = ', test_milestone.irr)
print('npv = ', test_milestone.npv)
print('multiple = ', test_milestone.multiple)
print('upfront = ', test_milestone.upfront)
print(test_milestone.cash_flows)
'''
