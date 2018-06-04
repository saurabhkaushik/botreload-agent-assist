var ticket_data = {id : 0, description:'', comment:'', comments: '', currentUser:'', subject:'', assignee:'', requester:'' , currentAccount:''};
var feedback_data = {selected_response_id : 0, ticket_data : ''};
var past_ticket_data = {upload_ticket_data : [], upload_comment_data : [], ticket_data : ''};
var response_data = {server_response : ''};

var context;
var client = ZAFClient.init();
var SERVER_NAME = 'https://br-aa-srv-prod.appspot.com';
var header = 'Hi ';
var footer = '<br><br>Thanks, <br> - ';
var called_flag = false;
var ticket_flag = false;
var ticket_list = [];
var comment_list = [];
var iter_ticket = 0;
var iter_comment = 0;
var max_tickets = 10;
var max_comments = 100;
var timeout_comment = 5000;

$(function() {
  client = ZAFClient.init();
  client.invoke('resize', { width: '100%', height: '400px' });
  firstData();
});

function setKey(key, val) {
	return localStorage.setItem("BL_SmartReply:" + key, val);
}

function getKey(key) {
   return localStorage.getItem("BL_SmartReply:" + key);
}

if (getKey("ticketflag") == null) {
	setKey("ticketflag", Date.now());
	ticket_flag = true;
} else {
	var difference = Date.now() - getKey("ticketflag");
    var daysDifference = Math.floor(difference/1000/60/60/24);
	if (daysDifference > 1) {
		ticket_flag = true;
	} else {
		ticket_flag = false;
	}
}

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
		//console.log('app.registered:');		
		if (called_flag == false) {
			called_flag = true;
			getTicketData();
			//syncAllTicketData(ticket_url);
		} else {
			return;
		}		
	});

function showInfo(data) {
	//console.log('showInfo:');
	var source = $("#add_task-hdbs").html();
	var template = Handlebars.compile(source);
	if (data.length > 0) {
		context = {comments: data, error: ''};
	} else {
		context = {comments: data, error: 'Sorry, Could not suggest any response for this.'};
	}
	var html = template(context);
	$("#content").html(html);
}

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

function sendPortal(event) {
	//console.log('applyComment:');
	url = SERVER_NAME + '/smartreply/route?cust_id=' + ticket_data.currentAccount.subdomain;
	window.open(url,'_blank');
};

function getResponseData() {
	//console.log('getResponseData:', ticket_data); //JSON.stringify(ticket_data));
	var settings = {
	    url: SERVER_NAME +'/intent',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(ticket_data),
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

function syncTicketData() {	
	//console.log('syncTicketData:', past_ticket_data); //JSON.stringify(past_ticket_data));
	var settings = {
	    url: SERVER_NAME +'/uploadtickets',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(past_ticket_data),
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
	console.log('syncFeedbackData:', feedback_data); // JSON.stringify(feedback_data));
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

function getTicketData() {	
	if (ticket_flag == false )
		return;
	//console.log('getTicketData:');
	var settings = {
		url: '/api/v2/tickets.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	};

	client.request(settings).then(
    function(data) {
        //console.log(data);
    	past_ticket_data.upload_ticket_data = data.tickets
    	past_ticket_data.ticket_data = ticket_data
    	for (i = 0; i < data.tickets.length; i++) {
    	   	if (iter_comment++ < max_comments) {
    	   		getCommentData(data.tickets[i]);    	
    	   	}
    	}
    	past_ticket_data.upload_comment_data = comment_list;
        setTimeout( function() {
        	syncTicketData();
        	}, timeout_comment);
    	//syncTicketData();
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}

function getCommentData(tickets_x) {
	//console.log ('getCommentData : ');
	var settings = {
		url: '/api/v2/tickets/'+ tickets_x.id + '/comments.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json',
	    tick_id : tickets_x.id
	}; 		
	client.request(settings).then(
    function(data) {
    	var comment_struct = {id: tickets_x.id, comments : data.comments}
    	comment_list.push(comment_struct);
    	return;
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}
