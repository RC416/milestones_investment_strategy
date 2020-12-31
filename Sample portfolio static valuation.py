# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 21:31:30 2019

Create multiple milestones and simulate a porfolio
Use sample values and one outcome scenario

@author: Ray
"""

from Milestone_class import Milestone 
from Milestone_class import cumulative_probs
from Milestone_class import portfolio_cfs
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

events = ['phase 1 init', 'phase 2 init', 'phase 3 init', 'approval']
values = [3.5, 7.0, 14.0, 19.0]
timing = [1, 3, 5, 8]
stage_prob = [0.320, 0.632, 0.307, 0.496]
discount_rate = 0.15

#create a portfolio of 5 milestones
# choose the number of milestones in 5 deals

#n_milestones = random.choices([2,3,4], weights=None, k=5)
n_milestones_sample = [2,3,3,4,4]

# events selected given number of milestones
events_sample = [events[-2:],events[-3:],events[-3:],events[-4:],events[-4:]]

#values generated as multiples 1-2x of initial values
values_sample = [[19,26],[13,26,35],[13,26,36],[4,8,16,22],[6,12,24,33]]

#timing according to what milestones are remaining
timing_sample = [[1,4],[1,3,6],[1,3,6],[1,3,5,8],[1,3,5,8]]

#probability take from stage_prob
probability_sample = [cumulative_probs(stage_prob[-2:]),cumulative_probs(stage_prob[-3:]),
                      cumulative_probs(stage_prob[-3:]),cumulative_probs(stage_prob[-4:]),
                      cumulative_probs(stage_prob[-4:])]

#a single outcome is used for this example. This one is a typical result
outcomes_sample = [[0, 0], [1, 0, 0], [1, 0, 0], [0, 0, 0, 0], [1, 1, 0, 0]]
#generated with: outcomes_sample = [generate_outcome(n_milestones_sample[x]) for x in range(0,5)]


#given the above static parameters, calculate outputs for a porfolio of
#these milestones given the chosen outcomes

deal_upfronts = []
deal_payouts = []
deal_multiples = []
deal_irrs = []
cash_flows = pd.DataFrame({'timing':[], 'payouts':[]})

# calculate return metrics and cash flows for each of the 5 milestones
for n in range(0,5):
    
    deal = Milestone(events_sample[n], values_sample[n], timing_sample[n], probability_sample[n], outcomes_sample[n])
    deal.valuation(discount_rate)
    
    deal_upfronts.append(deal.upfront)
    deal_payouts.append(deal.payout)
    deal_multiples.append(deal.multiple)
    deal_irrs.append(deal.irr)
    cash_flows = pd.concat([cash_flows, deal.cash_flows])
    print(deal.cash_flows)

# compile results in a table
deal_results = pd.DataFrame({'Events':events_sample, 'Values':values_sample,
                             'Timing':timing_sample, 'Probabilities':probability_sample,
                             'Outcomes':outcomes_sample, 'Upfront':deal_upfronts,
                             'Payouts':deal_payouts, 'Multiple':deal_multiples, 'IRR':deal_irrs})

# calculate portfolio IRR. see function documentation
#takes the table of total cash flows and converts to list with timing
portfolio_cfs = portfolio_cfs(cash_flows)
portfolio_irr = np.irr(portfolio_cfs)

#compile portfolio results
portfolio_results = pd.DataFrame({'Upfront':[deal_results['Upfront'].sum()], 'Payouts':[deal_results['Payouts'].sum()],
                                'Multiple':[deal_results['Payouts'].sum() / deal_results['Upfront'].sum()],
                                'IRR':[portfolio_irr]})


# plot cash flows
plt.bar(range(len(portfolio_cfs)), portfolio_cfs)
plt.xlabel('Year')
plt.title('Porfolio Cash Flows')
plt.xticks(range(len(portfolio_cfs)))
plt.yticks([])

def add_bar_labels(y_values):
    for x in range(len(y_values)):
        if y_values[x] > 0:
           plt.text(x, y_values[x], round(y_values[x],1), ha='center', va='bottom')
        if y_values[x] < 0:
           plt.text(x,y_values[x],round(y_values[x],1), ha='center', va='top')
    plt.ylim(min(y_values)*1.3, max(y_values)*1.3)

add_bar_labels(portfolio_cfs)
plt.show()