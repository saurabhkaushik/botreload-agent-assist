$(document).ready( function() {
    app.initialized()
        .then(function(_client) {
          var client = _client;
          client.events.on('app.activated',
            function() {
                client.data.get('contact')
                    .then(function(data) {
                        $('#apptext').text("Ticket created by " + data.contact.name);
                        firstData();

                    })
                    .catch(function(e) {
                        console.log('Exception - ', e);
                    });
        });
    });
});

var ticket_data = {id : 0, description:'', comment:'', currentUser:'', subject:'', assignee:'', requester:'' , currentAccount:''};
var feedback_data = {selected_response_id : 0, ticket_data : ''};
var response_data = {server_response : ''};

var context;
var client = ZAFClient.init();
var SERVER_NAME = '104.196.175.24';
var header = 'Hi ';
var footer = '<br><br>Thanks, <br> - ';


function firstData() {
	console.log('firstData:');
	Promise.all([client.get('ticket.id'),
	  			client.get('ticket.description'), 
	  			client.get('currentUser'),
	  			client.get('ticket.subject'),
	  			client.get('ticket.assignee.user'),
	  			client.get('ticket.requester.name'),
	  			client.get('currentAccount')]).then(
				  function fullfilled(contents){
					  ticket_data.id = contents[0]['ticket.id'];
					  ticket_data.description = contents[1]['ticket.description'];
					  ticket_data.currentUser = contents[2]['currentUser'];
					  ticket_data.subject = contents[3]['ticket.subject'];
					  ticket_data.assignee = contents[4]['ticket.assignee.user'];
					  ticket_data.requester = contents[5]['ticket.requester.name'];
					  ticket_data.currentAccount = contents[6]['currentAccount'];
					  getResponseData(client);
					  }
	  );
}

client.on('app.registered', function(appData) {
		getTicketData();
	});

function showInfo(data) {
	console.log('showInfo:');
	var source = $("#add_task-hdbs").html();
	var template = Handlebars.compile(source);
	context = {comments: data};
	var html = template(context);
	$("#content").html(html);
}

function showPostApply(data) {	
	console.log('showPostApply:');
	var source = $("#post-apply-template").html();
	var template = Handlebars.compile(source);
	context = {comments: data};
	var html = template(context);
	$("#content").html(html);
}

function applyComment(event, id, kid) {
	console.log('applyComment:');
	var comment_data = header + ticket_data.requester + ', <br><br>' + context.comments[kid].comment + footer + ticket_data.currentUser['name'];
	//console.log(comment_data);
	client.invoke('comment.appendHtml', comment_data);
    client.invoke('notify', 'Comment added to Ticket.');
    showPostApply();
    feedback_data.selected_response_id = id;
    feedback_data.ticket_data = ticket_data;
    uploadFeedbackData(feedback_data);
};

function showError() {
	console.log('showError:');
	var error_data = {
			'status': 404,
			'statusText': 'Not found'
	};
	var source = $("#error-template").html();
	var template = Handlebars.compile(source);
	var html = template(error_data);
	$("#content").html(html);
}

function getResponseData(client) {
	console.log('getResponseData:');
	var query_data = ticket_data;
	//console.log(ticket_data);
	var resp_data = '';
	var settings = {
	    url: 'http://'+ SERVER_NAME +'/intent',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(query_data),
	    dataType: 'json'
	  }; 

	client.request(settings).then(
	    function(data) {
	      client.invoke('notify', 'Received Ticket Responses.');
	      response_data.server_response = data;
	      showInfo(data);	      
	    },
	    function(response) {
	      var msg = 'Error ' + response.status + ' ' + response.statusText;
	      client.invoke('notify', msg, 'error');
	      console.log('getResponseData:'+response);
	      showError()
	    }
	);
}

function getTicketData(){
	console.log('getTicketData:');
	var settings = {
		url: '/api/v2/tickets.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 

	client.request(settings).then(
    function(data) {
      //console.log(data);
    	uploadTicketData(data); 
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ response);
    }
	);
}

function uploadTicketData(tickets) {
	console.log('uploadTicketData:');
	var settings = {
	    url: 'http://'+ SERVER_NAME +'/uploadtickets',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(tickets),
	    dataType: 'json'
	  }; 
	client.request(settings).then(
    function(data) {
      //client.invoke('notify', 'Received Ticket Responses.');
      //console.log(data);
      //console.log('uploadTicketData: Success');
    },
    function(response) {
      //var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('uploadTicketData:'+response);
    }
  );
}

function uploadFeedbackData() {
	console.log('uploadFeedbackData:');
	var settings = {
	    url: 'http://'+ SERVER_NAME +'/feedbkloop',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(feedback_data),
	    dataType: 'json'
	  }; 
	client.request(settings).then(
    function(data) {
      //client.invoke('notify', 'Received Ticket Responses.');
      //console.log(data);
      //console.log('uploadFeedbackData: Success');
    },
    function(response) {
      //var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('uploadFeedbackData:'+response);
    }
  );
}

