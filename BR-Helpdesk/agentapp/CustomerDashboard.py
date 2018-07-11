import dash
import dash_core_components as dcc
import dash_html_components as html
from agentapp.tickets_learner import tickets_learner

class CustomerDashboard(object): 
    
    def __init__(self, dash_app):
        self.dash_app = dash_app
        
    def appLayout(self): 
        data = [
            {
                'values': [10,90],
                'type': 'pie',
            },
        ]
        self.dash_app.layout= html.Div([
            dcc.Graph(
                id='graph',
                figure={
                    'data': data,
                    'layout': {
                        'margin': {
                            'l': 30,
                            'r': 0,
                            'b': 30,
                            't': 0
                        },
                        'legend': {'x': 0, 'y': 1}
                    }
                }
            )
        ])
    
    def chartDisplay(self, cust_id): 
        print ('chartDisplay : ')
        ticket_learn = tickets_learner() 
        analytic_data = ticket_learn.getAnalyticsData(cust_id)
        for linestms in analytic_data:           
            print (linestms)
            if len(linestms) > 0: 
                ticket_served = linestms[0]['ticket_total_count']
                ticket_applied = linestms[0]['Feedback_tickets_count']
                response_total = linestms[0]['response_total_count']
                response_served = linestms[0]['response_modified_count']
                response_applied = linestms[0]['response_default_count']
        data = [
            {
                'values': [ticket_served,ticket_applied],
                'type': 'pie',
                'labels' : ['ticket_served','ticket_applied'],
                'hole' : .4,
            },
            ]        
        self.dash_app.layout = html.Div([
            dcc.Graph(
                id='graph',
                figure={
                    'data': data,
                    'layout': {
                        'margin': {
                            'l': 30,
                            'r': 0,
                            'b': 30,
                            't': 0
                        },
                        'legend': {'x': 0, 'y': 1} 
                        } 
                    }
                )
            ]
        )
        return self.dash_app.index()
