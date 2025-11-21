# Visualization-of-shipping-volume

## One pager:

### ***Briefly describe the background. Summarize business opportunities and market situation. Origin of request.***
Lindab has a shared system for booking transorts where correct data on volume is very important to achieve a high load factor. 
By utilizing data science, a more effective un/loading process and a higher load factor per logistical order could be achieved. Increasing the effectiveness of the transport process directly correlates with cost savings and increased environmental sustainability.
Describe the purpose.

### ***The purpose should be expressed as a description of the general aim and direction, and the expected effect.***
Currently Lindab lacks a tool for visualizing the packages and parcels of logistic orders. A visualization tool can provide an automatic, fast and effective way to show how items can be loaded in trucks


**The purpose of this tool is to:**
**Improve the workprocess of transport by:**
- Automatically create a visualization with an suggestion of how items can be loaded in trucks
- Provide an interactable 3d visualization tool of the loading of items in trucks
- Provide a more accurate volume calculation of logistic orders (cost saving and environmental sustainability)
**Improve communcations down the supply chain by:**
- Forwarding the visualization alongside the logistic order
**Prepare for future implementation of ML/AI logistical order assistance by:**
In order to implement a Lindab trained ML/AI model, data on how Lindabs transport process currently works is needed. The current data on logistial orders and packages is unfortunetly not enough.

Using a visualization tool, training data on the decision processes of logistical orders can be generated. This data can answer the important question of which and how logistical orders can be consolidated to achieve a higher load factor. The data can also be used to train a model to suggest how the loading of packages and parcles can be done in a specific logistical order.

***The expected effect is:***
- Decreased time spent per logistic order (volume calculation and load planning), 
- Reduced transport costs by increaseing the capabilities of the Transport Office and the Control Tower 
- Increase communcation down the supply chain 
- Preparing data for a future ML/AI logistical order assistant



### ***State the expected outcome, including limits for time, cost and method.*** 
The expected outcome is a standalone program built with python which can select transport orders and visualize them in a 3d-view. This view, along with each item of the transport order, should be interactable and customizable.



### ***Method***  
This will be developed as an agile project with sprints using the Microsoft Planner in the team Data Scientist LIA

**Overview of steps:**
1. Aquire domain knowledge of Lindabs databases and transport process 
2. Aquire permissions to TM and data related to the transport process 
3. Develop the visualization tool
4. Implement a test database of packaged item and truck data. 
6. Gain feedback on visualization test from Control Tower
6. Introduce suggestion of loading into the visualization 
7. Gain feedback on test from transport office in Profil Förslöv and Control Tower Apply improvments from feedback 
8. Prep for AI/ML assistant

**Overview of sprints:**
1. Research and POC 
2. Steering group meeting 
3. Basic visualization tool 
4. Connect to real time data 
5. Implement loading suggestions 
6. Go live in Control Tower 
7. Go live in Transport Office (Sweden) 
8. Prep for AI/ML assistant 

More detailed overview of sprints can be found in teams "original overview of agile planning.png"



### ***Dependencies to other projects:***
None (TM or Control Tower?)
