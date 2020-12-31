# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 13:34:40 2019

Same as the first valuation. This one assumes that the phase 1 milestone
has already been achieved. 

@author: Ray
"""
from Milestone_class import Milestone 
#created an object to store and do calculations
from Milestone_class import cumulative_probs
import pandas as pd

# create and value a pre-clinical milestone deal

# initialize milestone object with pre-clinical milestones 
events = ['phase 3 init', 'approval']
values = [14.0, 19.0]
timing = [1, 3]
stage_prob = [0.307, 0.496]
discount_rate = 0.15

PC_deal = Milestone(events, values, timing, cumulative_probs(stage_prob))

# Look at returns under various scenarios (which milestones pay out)

# all possible scenarios ranging from all to zero milestones hitting
outcomes = [[1,1],
            [1,0],
            [0,0],]
            
scenario = ['approval', 'phase 3', 'none']
face_value = values
upfront = []
payout = []
npv = []
multiple = []
irr = []
proba = cumulative_probs(stage_prob)
proba.insert(0, 1 - stage_prob[0])
proba.reverse()

for outcome in outcomes:  

    PC_deal.valuation(discount_rate=discount_rate, outcomes=outcome)
    
    payout.append(PC_deal.payout)
    npv.append(PC_deal.npv)
    multiple.append(PC_deal.multiple)
    irr.append(PC_deal.irr)

upfront = PC_deal.data['NPV evs'].tolist()
upfront.reverse()
upfront.append(0)

results = pd.DataFrame({'Scenario':scenario, 'Probability':proba, 
                        'Payout':payout, 'Multiple':multiple, 
                        'IRR':irr, 'Upfront':upfront})

print(PC_deal.data)
