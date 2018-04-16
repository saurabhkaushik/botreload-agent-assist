var ticket_data = {id : 0, description:'', comment:'', comments: '', currentUser:'', subject:'', assignee:'', requester:'' , currentAccount:''};
var feedback_data = {selected_response_id : 0, ticket_data : ''};
var response_data = {server_response : ''};

var context;
var client = ZAFClient.init();
var SERVER_NAME = 'https://br-aa-srv-prod.appspot.com'; 
var header = 'Hi ';
var footer = '<br><br>Thanks, <br> - ';

$(function() {
  client = ZAFClient.init();
  client.invoke('resize', { width: '100%', height: '400px' });
  firstData();
});

function firstData() {
	//console.log('firstData:');
	Promise.all([client.get('ticket'),
	  			client.get('currentUser'),
	  			client.get('currentAccount')]).then(
				  function fullfilled(contents){
					  ticket_data.id = contents[0]['ticket']['id'];
					  ticket_data.description = contents[0]['ticket']['description'];
					  ticket_data.subject = contents[0]['ticket']['subject'];
					  ticket_data.assignee = contents[0]['ticket']['assignee']['user'];
					  ticket_data.requester = contents[0]['ticket']['requester'];
					  ticket_data.comments = contents[0]['ticket']['comments'];
					  ticket_data.currentUser = contents[1]['currentUser']['name'];
					  ticket_data.currentAccount = contents[2]['currentAccount'];
					  //console.log ('ticket_data : ' + JSON.stringify(ticket_data));
					  getResponseData(client);
					  }
	  ).catch(function(error) {
		  console.log(error.toString()); 
	  });
}

client.on('app.registered', function(appData) {
		getTicketData();
	});

function showInfo(data) {
	//console.log('showInfo:');
	var source = $("#add_task-hdbs").html();
	var template = Handlebars.compile(source);
	context = {comments: data};
	var html = template(context);
	$("#content").html(html);
}

function showPostApply(data) {	
	//console.log('showPostApply:');
	var source = $("#post-apply-template").html();
	var template = Handlebars.compile(source);
	context = {comments: data};
	var html = template(context);
	$("#content").html(html);
}

function applyComment(event, id, kid) {
	//console.log('applyComment:');
	var comment_data = header + ticket_data.requester['name'] + ', <br><br>' + context.comments[kid].comment + footer + ticket_data.currentUser;
	client.invoke('comment.appendHtml', comment_data);
    client.invoke('notify', 'Comment added to Ticket.');
    showPostApply();
    feedback_data.selected_response_id = id;
    feedback_data.ticket_data = ticket_data;
    syncFeedbackData(feedback_data);
};

function showError() {
	//console.log('showError:');
	var error_data = {
			'status': 404,
			'statusText': 'Not found'
	};
	var source = $("#error-template").html();
	var template = Handlebars.compile(source);
	var html = template(error_data);
	$("#content").html(html);
}

function getResponseData() { 
	//console.log('getResponseData:');
	var query_data = ticket_data;
	var resp_data = '';
	var settings = {
	    url: SERVER_NAME +'/intent',
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
	      console.log('getResponseData:' + msg);
	      showError()
	    }
	);
}

var called_flag = false;
function getTicketData(){
	if (called_flag == false) {
		called_flag = true;
	} else {
		return;
	}
	var settings = {
		url: '/api/v2/tickets.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 

	client.request(settings).then(
    function(data) {
        //console.log(data);
    	syncTicketData(data); 
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}

function syncTicketData(tickets) {
	//console.log('syncTicketData:');
	var settings = {
	    url: SERVER_NAME +'/uploadtickets',
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
      //console.log('syncTicketData: Success');
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('syncTicketData:' + msg);
    }
  );
}

function syncFeedbackData() {
	//console.log('syncFeedbackData:');
	var settings = {
	    url: SERVER_NAME +'/uploadfeedback',
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
      //console.log('syncFeedbackData: Success');
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('syncFeedbackData:' + msg);
    }
  );
}
