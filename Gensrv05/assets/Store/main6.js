var ticket_data = {id : 0, description:'', comment:''};
var context;
var client = ZAFClient.init();

$(function() {
  client = ZAFClient.init();
  client.invoke('resize', { width: '100%', height: '400px' });
  
  firstData();
  //getResponseData(ticket_data.description, client);
});

function firstData() {
  Promise.all([client.get('ticket.id'),client.get('ticket.description')]).then(
	  function fullfilled(contents){
		  ticket_data.id = contents[0]['ticket.id'];
		  ticket_data.description = contents[1]['ticket.description'];
		  getResponseData(ticket_data.description, client);
		  }
	  );
}
/*
client.on('app.registered', function(appData) {
	  // In order to render the translated strings the Agents locale
		getHistoricalData();
		getAllTags();
	});

client.on('app.activated', function(appData) {
  // In order to render the translated strings the Agents locale
	getHistoricalData();
	getAllTags();
});*/
	
function getHistoricalData(){
	console.log('getHistoricalData:');
	var settings = {
		url: '/api/v2/tickets.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 

	client.request(settings).then(
    function(data) {
      console.log(data);
      uploadTickets(data);
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      client.invoke('notify', msg, 'error');
    }
	);
}

function getAllTags(){
	console.log('getAllTags:');
	var settings = {
		url: '/api/v2/tags.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 

	client.request(settings).then(
    function(data) {
      console.log(data);
      uploadTags(data);
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      client.invoke('notify', msg, 'error');
    }
	);
}

function showInfo(data) {
  var source = $("#add_task-hdbs").html();
  var template = Handlebars.compile(source);
  context = {comments: data	};
  var html = template(context);
  $("#content").html(html);
}

function applyComment(event, id, comment) {
	client.set('comment.text', context.comments[id].comment);
    client.invoke('notify', 'Comment added to Ticket.');
};

function showError() {
  var error_data = {
    'status': 404,
    'statusText': 'Not found'
  };
  var source = $("#error-template").html();
  var template = Handlebars.compile(source);
  var html = template(error_data);
  $("#content").html(html);
}

function getResponseData(task, client) {
	var resp_data = '';
	var settings = {
	    url: 'http://13.71.115.220/intent',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(task),
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
    }
  );
}

function uploadTickets(tickets) {
	console.log('uploadTickets:');
	var settings = {
	    url: 'http://13.71.115.220/uploadtickets',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(tickets),
	    dataType: 'json'
	  }; 
	client.request(settings).then(
    function(data) {
      //client.invoke('notify', 'Received Ticket Responses.');
      console.log(data);
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      client.invoke('notify', msg, 'error');
    }
  );
}

function uploadTags(tags) {
	console.log('uploadTags:');
	var settings = {
	    url: 'http://13.71.115.220/uploadtags',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(tags),
	    dataType: 'json'
	  }; 
	client.request(settings).then(
    function(data) {
      //client.invoke('notify', 'Received Ticket Responses.');
      console.log(data);
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      client.invoke('notify', msg, 'error');
    }
  );
}