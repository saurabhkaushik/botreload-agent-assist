var ticket_data = {id : 0, description:'', comment:'', currentUser:'', subject:'', assignee:'', requester:'' };
var context;
var client = ZAFClient.init();
var SERVER_NAME = '13.71.115.220';
var header = 'Hello ';
var footer = 'Regards, \n';

$(function() {
  client = ZAFClient.init();
  client.invoke('resize', { width: '100%', height: '400px' });
  firstData();
});

function firstData() {
	console.log('firstData:');
	Promise.all([client.get('ticket.id'),
	  			client.get('ticket.description'), 
	  			client.get('currentUser'),
	  			client.get('ticket.subject'),
	  			client.get('ticket.assignee.user'),
	  			client.get('ticket.requester.name')]).then(
				  function fullfilled(contents){
					  ticket_data.id = contents[0]['ticket.id'];
					  ticket_data.description = contents[1]['ticket.description'];
					  ticket_data.currentUser = contents[2]['currentUser'];
					  ticket_data.subject = contents[3]['ticket.subject'];
					  ticket_data.assignee = contents[4]['ticket.assignee.user'];
					  ticket_data.requester = contents[5]['ticket.requester.name'];
					  getResponseData(client);
					  }
	  );
}

client.on('app.registered', function(appData) {
		getTicketData();
		getTagData();
	});



function showInfo(data) {
	console.log('showInfo:');
	var source = $("#add_task-hdbs").html();
	var template = Handlebars.compile(source);
	context = {comments: data	};
	var html = template(context);
	$("#content").html(html);
}

function showPostApply(data) {	
	console.log('showPostApply:');
	var source = $("#post-apply-template").html();
	var template = Handlebars.compile(source);
	context = {comments: data	};
	var html = template(context);
	$("#content").html(html);
}

function applyComment(event, id) {
	console.log('applyComment:');
	var comment_data = header + ticket_data.requester + ', \n' + context.comments[id].comment + footer + '. \n' + ticket_data.currentUser['name'];
	//console.log(comment_data);
	client.set('comment.text', comment_data);
    client.invoke('notify', 'Comment added to Ticket.');
    showPostApply();
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
	var query_data = ticket_data.subject + ' . ' + ticket_data.description;
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

function getTagData(){
	console.log('getTagData:');
	var settings = {
		url: '/api/v2/tags.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 

	client.request(settings).then(
    function(data) {
      //console.log(data);
      uploadTagData(data);
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

function uploadTagData(tags) {
	console.log('uploadTagData:');
	var settings = {
	    url: 'http://'+ SERVER_NAME +'/uploadtags',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(tags),
	    dataType: 'json'
	  }; 
	client.request(settings).then(
    function(data) {
      //client.invoke('notify', 'Received Ticket Responses.');
      //console.log(data);
      //console.log('uploadTagData: Success');
    },
    function(response) {
      //var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('uploadTagData:'+response);
    }
  );
}