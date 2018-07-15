import dash
import dash_core_components as dcc
import dash_html_components as html
from agentapp.tickets_learner import tickets_learner
from textwrap import dedent

class CustomerDashboard(object): 
    
    def __init__(self, dash_app):
        self.dash_app = dash_app
        self.dash_app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501
        self.dash_app.css.append_css({'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css'})  # noqa: E501

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
                response_modified = linestms[0]['response_modified_count']
                response_default = linestms[0]['response_default_count']
                response_new = int(response_total - (response_modified + response_default))
        ticket_data = [
            {
                'values': [ticket_served, ticket_applied],
                'type': 'pie',
                'labels' : ['ticket_served', 'ticket_applied'],
                'hole' : .4,
            },
            ]  
        response_data = [
            {
                'values': [response_modified, response_default, response_new],
                'type': 'pie',
                'labels' : ['response_modified', 'response_default', 'response_new'],
                'hole' : .4,
            },
            ]       
        self.dash_app.layout = html.Div(children=[  
             
            html.Div([
                html.A(html.Button('Back to Smart Reply Portal ', style={'background-color' : '#4CAF50', 'color' : 'white'}),
                       href='/smartreply/list?cust_id='+str(cust_id)),
                html.H3('Ticket - Served vs Applied:'),
                dcc.Graph(
                    id='graph1',
                    figure={
                        'data': ticket_data,
                        'layout': {
                            'legend': {'x': 0, 'y': 1} 
                            },
                        'title' :'Gender Distribution'
                        },
                    style={'width': '600'}
                    )], style={'display': 'inline-block'}),                      
            html.Div([
                html.H3('Response - Default vs Modified vs News:'),
                dcc.Graph(
                id='graph2',
                figure={
                    'data': response_data,
                    'layout': {
                        'legend': {'x': 0, 'y': 1} 
                        },
                    'title' :'Gender Distribution'
                    },
                style={'width': '600'}
                )], style={'display': 'inline-block'})
            ],  style={'width': '100%', 'display': 'inline-block'})
        return self.dash_app.index()
