# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 21:12:50 2019

@author: Ray
"""

import pandas as pd
import numpy as np

pd.set_option('display.max_columns',15)
pd.set_option('display.width', 200)


class Milestone:
    def __init__(self, events, value, timing, probabilities=None, outcomes=None):
        self.events = events
        self.value = value
        self.timing = timing
        self.outcomes = outcomes
        
        self.data = pd.DataFrame({'events':events,'value':value,'timing':timing, 
                                  'probabilities':probabilities, 'evs':None, 'outcomes':outcomes,
                                  'payouts':None, 'NPV':None, 'NPV evs':None})
        
        self.data['payouts'] = self.data['outcomes'] * self.data['value']
        self.data['evs'] = self.data['probabilities'] * self.data['value']
        
    def valuation(self, discount_rate=0.10):
        
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
       
        self.multiple = self.data['payouts'].sum() / self.data['NPV evs'].sum()

    def cash_flows(self):
        return self.data.loc[self.data['outcomes'] != 0, ('timing', 'payouts')]
      


events = ['phase 1', 'phase 2', 'phase 3', 'approval']
value = [10, 20, 50, 100]
timing = [1, 3, 5, 7]
cumulative_probabilities = [0.35, 0.20, 0.13, 0.10]
outcomes = [1, 1, 0, 0]

test_milestone = Milestone(events, value, timing, cumulative_probabilities, outcomes)

print(test_milestone.data)

test_milestone.valuation()
print(test_milestone.data)
print(test_milestone.npv)
print(test_milestone.multiple)
print(test_milestone.cash_flows())
