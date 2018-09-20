var ticket_data = {id : 0, description:'', comment:'', comments: '', currentUser:'', subject:'', assignee:'', requester:'' , currentAccount:''};
var feedback_data = {selected_response_id : 0, selected_response_prob : 0, ticket_data : ''};
var past_ticket_data = {upload_ticket_data : [], upload_comment_data : [], ticket_data : ''};
var article_data = {article_data : '', ticket_data : ''};
var response_data = {server_response : ''};

var SERVER_NAME = 'https://botreloadprod004.appspot.com';
//var SERVER_NAME = 'https://botreloaddev004.appspot.com';

var context;
var client = ZAFClient.init();
var header = 'Hi ';
var footer = '<br><br>Thanks and Regards, <br> - ';
var called_flag = false;
var ticket_flag = false;
var server_ticket_flag = false;
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
			//getServerTicketFlag();
			setTimeout( function() {
				getServerTicketFlag();
	        	}, timeout_comment);
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

function applyComment(event, id, prob, kid) {
	//console.log('applyComment:');
	var comment_data = header + ticket_data.requester['name'] + ', <br><br>' + context.comments[kid].comment + footer + ticket_data.currentUser;
	client.invoke('comment.appendHtml', comment_data);
    client.invoke('notify', 'Comment added to Ticket.');
    showPostApply();
    feedback_data.selected_response_id = id;
    feedback_data.selected_response_prob = prob;
    feedback_data.ticket_data = ticket_data;
    sendFeedbackData(feedback_data);
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
	      //console.log('getResponseData:' + msg);
	      showError()
	    }
	);
}

function getServerTicketFlag() {
	//console.log('getServerTicketFlag:', ticket_data); // JSON.stringify(feedback_data));
	var settings = {
	    url: SERVER_NAME +'/getticketflag',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(ticket_data),
	    dataType: 'json'
	  };
	client.request(settings).then(
		function(data) {
			//console.log('Received Ticket Flag Responses.', data);
		    server_ticket_flag = data['Ticket_Flag'];
		    //console.log (server_ticket_flag)
		    getTicketData(data);
		    },
		    function(response) {
		    	var msg = 'Error ' + response.status + ' ' + response.statusText;
		    	client.invoke('notify', msg, 'error');
		    	console.log('getServerTicketFlag:' + msg);
		    	getTicketData();
		    }
	);
}
function sendTicketData() {	
	//console.log('sendTicketData:', past_ticket_data); //JSON.stringify(past_ticket_data));
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
    	setKey("ticketflag", Date.now());
    	//client.invoke('notify', 'Received Ticket Responses.');
    	//console.log(data);
    	//console.log('sendTicketData: Success');
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      //console.log('sendTicketData:' + msg);
    }
  );
}

function sendFeedbackData() {
	//console.log('sendFeedbackData:', feedback_data); // JSON.stringify(feedback_data));
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
      //console.log('sendFeedbackData: Success');
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      //console.log('sendFeedbackData:' + msg);
    }
  );
}

function sendArticleData() {	
	//console.log('sendArticleData:', article_data); //JSON.stringify(article_data)); 
	var settings = {
	    url: SERVER_NAME +'/uploadarticles',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(article_data),
	    dataType: 'json'
	  };
	client.request(settings).then(
    function(data) {
    	setKey("ticketflag", Date.now());
    	//client.invoke('notify', 'Received Ticket Responses.');
    	//console.log(data);
    	//console.log('sendArticleData: Success');
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      //console.log('sendArticleData:' + msg);
    }
  );
}

function getTicketData() {	
	//console.log('getTicketData:');
	//ticket_flag = true;
	//server_ticket_flag=true;
	if (ticket_flag == false && server_ticket_flag == false)
		return;	
	var settings = {
		url: '/api/v2/tickets.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	};
	client.request(settings).then(
    function(data) {
        //console.log(data);
    	past_ticket_data.upload_ticket_data = data.tickets;
    	past_ticket_data.ticket_data = ticket_data;
    	for (i = 0; i < data.tickets.length; i++) {
    	   	if (iter_comment++ < max_comments) {
    	   		getCommentData(data.tickets[i]);
    	   	}
    	}
    	getArticleData();
    	past_ticket_data.upload_comment_data = comment_list;
        setTimeout( function() {
        	sendTicketData();
        	}, timeout_comment);
        setTimeout( function() {
        	sendArticleData();
        	}, (timeout_comment*2));
        //sendArticleData();
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      //console.log('Error : '+ msg);
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
    	var comment_struct = {id: data.id, comments : data.comments}
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

function getArticleData() {
	//console.log ('getArticlesData : ');
	var settings = {
		url: '/api/v2/help_center/articles.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	}; 		
	client.request(settings).then(
    function(data) {
    	article_data.article_data = data.articles;
    	article_data.ticket_data = ticket_data;
    	return;
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}
