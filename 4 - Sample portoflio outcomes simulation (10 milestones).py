# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 21:31:30 2019

Create multiple milestones and simulate a porfolio
this one has 10 milestones

@author: Ray
"""

from Milestone_class import Milestone, cumulative_probs, portfolio_cfs, generate_outcome
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
n_milestones_sample = [2,2,3,3,3,3,4,4,4,4]

# events selected given number of milestones
events_sample = [events[-2:],events[-2:],events[-3:],events[-3:],events[-3:],events[-3:],events[-4:],events[-4:],events[-4:],events[-4:]]

#values generated as multiples 1-2x of initial values
values_sample = [[19,26],[19,26],[13,26,35],[13,26,36],[13,26,35],[13,26,36],[4,8,16,22],[6,12,24,33],[4,8,16,22],[6,12,24,33]]

#timing according to what milestones are remaining
timing_sample = [[1,4],[1,4],[1,3,6],[1,3,6],[1,3,6],[1,3,6],[1,3,5,8],[1,3,5,8],[1,3,5,8],[1,3,5,8]]

#probability take from stage_prob
probability_sample = [cumulative_probs(stage_prob[-2:]),cumulative_probs(stage_prob[-2:]),
                      cumulative_probs(stage_prob[-3:]),cumulative_probs(stage_prob[-3:]),
                      cumulative_probs(stage_prob[-3:]),cumulative_probs(stage_prob[-3:]),
                      cumulative_probs(stage_prob[-4:]),cumulative_probs(stage_prob[-4:]),
                      cumulative_probs(stage_prob[-4:]),cumulative_probs(stage_prob[-4:])]

# create a random outcome set. Inner list creates one set of 5 outcomes, repeat many times
outcomes_sample = [[generate_outcome(n_milestones_sample[x], stage_prob) for x in range(0,10)] for x in range(0,10000)]


portfolio_results = pd.DataFrame({'Upfront':[], 'Payout':[], 'Multiple':[], 'IRR':[], 'Cash Flows':[]})


for outcome in outcomes_sample:
    
    cash_flows = pd.DataFrame({'timing':[], 'payouts':[]})
    deal_upfronts = []
    deal_payouts = []
    
    # build portfolio
    for n in range(0,10):
        deal = Milestone(events_sample[n], values_sample[n], timing_sample[n],
                         probability_sample[n], outcome[n])
        deal.valuation(discount_rate)
        
        deal_upfronts.append(deal.upfront)
        deal_payouts.append(deal.payout)
        cash_flows = pd.concat([cash_flows, deal.cash_flows])
        
    deal_results = pd.DataFrame({'Values':values_sample, 'Timing':timing_sample,
                                 'Upfront':deal_upfronts, 'Payouts':deal_payouts})

    
    portfolio_irr = np.irr(portfolio_cfs(cash_flows))
    upfront = sum(deal_upfronts)
    payout = sum(deal_payouts)
    multiple = payout / upfront

    port_result = pd.DataFrame({'Upfront':[upfront], 'Payout':[payout],
                                'Multiple':[multiple], 'IRR':[portfolio_irr],
                                'Cash Flows':[portfolio_cfs(cash_flows)]})
    
    portfolio_results = pd.concat([portfolio_results, port_result])

portfolio_results['IRR'].fillna(value=0, inplace=True) 

portfolio_results.to_csv('10 milestones 10k simulation.csv', index=False)

# plot distribution of outcome measures

plt.hist(portfolio_results['Payout'],bins=int(220/5), density=True)
plt.title('Payout')
plt.yticks([])
plt.xlim(0,250)
plt.show()

plt.hist(portfolio_results['IRR'],bins=40, density=True)
plt.title('IRR')
plt.xticks(ticks=[-0.5,0,0.5,1,1.5],labels=['-50%','0%','50%','100%','150%'])
plt.yticks([])
plt.show()

plt.hist(portfolio_results['Multiple'],bins=50, density=True)
plt.title('Multiple')
plt.xlim(0,6)
plt.yticks([])
plt.show()


multiples_sorted = portfolio_results['Multiple'].tolist()
multiples_sorted.sort()

plt.step(range(len(multiples_sorted)),multiples_sorted)
plt.show()


'''
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
'''



